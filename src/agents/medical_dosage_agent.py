"""Medical Dosage Agent with LangChain tool orchestration."""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MedicalDosageAgent:
    """Agent that routes requests through LangChain tools and Gemini when configured."""

    def __init__(self, rag_pipeline=None, memory_system=None):
        self.rag_pipeline = rag_pipeline
        self.memory_system = memory_system
        self.llm = None
        self.langchain_agent = None
        self.tools: List[Dict[str, Any]] = []

        self._attach_default_tools()
        self._try_init_langchain_agent()

        logger.info("Medical Dosage Agent initialized")

    def _attach_default_tools(self):
        """Attach deterministic compute tool and optional knowledge retrieval tool."""
        try:
            from tools.compute_dosage_tool import compute_dosage
        except ImportError:
            from ..tools.compute_dosage_tool import compute_dosage

        def dosage_calculator(weight_kg: float, drug_mg_per_kg: float, max_dose_mg: float) -> str:
            try:
                result = compute_dosage(weight_kg, drug_mg_per_kg, max_dose_mg)
                return json.dumps(result, default=str)
            except Exception as exc:
                return json.dumps({"error": str(exc)})

        self.tools.append(
            {
                "name": "compute_safe_dosage",
                "description": (
                    "Calculate safe medication dose using patient weight, mg/kg dose, and max dose."
                ),
                "func": dosage_calculator,
            }
        )

        if self.rag_pipeline:
            def retrieve_knowledge(query: str) -> str:
                results = self.rag_pipeline.retrieve(query, k=3)
                if not results:
                    return "No relevant medical knowledge found."

                formatted = []
                for item in results:
                    title = item["metadata"].get("title", "Unknown")
                    content = item["content"][:250]
                    formatted.append(f"- {title}: {content}...")
                return "\n".join(formatted)

            self.tools.append(
                {
                    "name": "search_medical_knowledge",
                    "description": "Search medical guidelines and dosage-related references.",
                    "func": retrieve_knowledge,
                }
            )

    def _try_init_langchain_agent(self):
        """Initialize LangChain v1 tool-calling agent when API key is available."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.info("GOOGLE_API_KEY not set; using deterministic fallback mode")
            return

        try:
            from langchain.agents import create_agent
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.tools import tool

            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                google_api_key=api_key,
            )

            @tool
            def compute_safe_dosage(weight_kg: float, drug_mg_per_kg: float, max_dose_mg: float) -> str:
                """Compute safe dose in mg from weight, mg/kg dosing, and max dose cap."""
                return self.tools[0]["func"](weight_kg, drug_mg_per_kg, max_dose_mg)

            langchain_tools = [compute_safe_dosage]

            if len(self.tools) > 1:
                @tool
                def search_medical_knowledge(query: str) -> str:
                    """Search relevant medical guidance for drugs, dosing, and safety constraints."""
                    return self.tools[1]["func"](query)

                langchain_tools.append(search_medical_knowledge)

            system_prompt = (
                "You are a medical logistics assistant. "
                "Always use tools for dosage calculations and knowledge lookup. "
                "Do not invent medication math. "
                "Return concise, safety-first responses."
            )

            self.llm = llm
            self.langchain_agent = create_agent(
                model=llm,
                tools=langchain_tools,
                system_prompt=system_prompt,
            )
            logger.info("LangChain tool-calling agent initialized")
        except Exception as exc:
            logger.warning("LangChain agent init failed; fallback mode active: %s", exc)
            self.langchain_agent = None

    def _extract_text_from_agent_result(self, result: Any) -> str:
        """Normalize LangChain result payload into plain text."""
        if isinstance(result, dict):
            if isinstance(result.get("output"), str):
                return result["output"]
            messages = result.get("messages", [])
            if messages:
                last = messages[-1]
                content = getattr(last, "content", "")
                if isinstance(content, list):
                    return " ".join(
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in content
                    ).strip()
                return str(content)
        return str(result)

    def _fallback_process(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Deterministic routing path used when Gemini/LangChain is unavailable."""
        # Dosage path
        if any(word in user_query.lower() for word in ["dosage", "dose", "calculate", "how much"]):
            numbers = re.findall(r"\d+\.?\d*", user_query)
            if len(numbers) >= 2:
                try:
                    weight = float(numbers[0])
                    dose_per_kg = float(numbers[1])
                    max_dose = float(numbers[2]) if len(numbers) > 2 else 500.0
                    result = json.loads(self.tools[0]["func"](weight, dose_per_kg, max_dose))
                    response_text = (
                        f"Safe dosage: {result['result']}mg\n\n{result['detail']}"
                        if "error" not in result
                        else f"Error: {result['error']}"
                    )

                    if self.memory_system and "error" not in result:
                        self.memory_system.add_dosage_record(
                            patient_weight=weight,
                            drug_mg_per_kg=dose_per_kg,
                            max_dose=max_dose,
                            calculated_dose=result["result"],
                            metadata={"source": "agent_fallback"},
                        )

                    return {
                        "success": True,
                        "response": response_text,
                        "tool_used": "compute_safe_dosage",
                        "query": user_query,
                    }
                except Exception as exc:
                    logger.error("Fallback dosage path failed: %s", exc)

        # Knowledge path
        if len(self.tools) > 1 and any(
            word in user_query.lower() for word in ["drug", "medication", "guideline", "contraindic"]
        ):
            response_text = self.tools[1]["func"](user_query)
            if self.memory_system:
                self.memory_system.add_conversation(user_query, response_text, context)
            return {
                "success": True,
                "response": response_text,
                "tool_used": "search_medical_knowledge",
                "query": user_query,
            }

        return {
            "success": True,
            "response": (
                "I can help with dosage calculations and medical guidance retrieval. "
                "Please include patient weight (kg), dose (mg/kg), and optional max dose (mg)."
            ),
            "tool_used": "help",
            "query": user_query,
        }

    def process_request(self, user_query: str, context: Dict = None) -> Dict[str, Any]:
        """Process requests through LangChain agent when available, otherwise fallback."""
        try:
            if self.langchain_agent:
                result = self.langchain_agent.invoke(
                    {"messages": [{"role": "user", "content": user_query}]}
                )
                response_text = self._extract_text_from_agent_result(result)

                if self.memory_system:
                    self.memory_system.add_conversation(user_query, response_text, context)

                return {
                    "success": True,
                    "response": response_text,
                    "tool_used": "langchain_tool_calling_agent",
                    "query": user_query,
                    "context": context or {},
                }

            return self._fallback_process(user_query, context)
        except Exception as exc:
            logger.error("Error processing request: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "response": f"An error occurred: {str(exc)}",
            }

    def get_tools_info(self) -> List[Dict[str, str]]:
        """Return currently available tools."""
        return [{"name": tool["name"], "description": tool["description"]} for tool in self.tools]
