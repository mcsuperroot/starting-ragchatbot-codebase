import groq


class AIGenerator:
    """Handles interactions with Groq's API for generating responses"""

    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to search tools.

Search Tools:
- search_course_content: Search local course materials (use first for course-related questions)
- search_web: Search the web (use when local course materials don't have the answer)

Search Strategy:
- For course-specific questions: Use search_course_content first
- If local search yields no results or is insufficient: Use search_web to find information online
- **One search per query maximum**

Response Protocol:
- **General knowledge questions**: Use search_web to find current information
- **Course-specific questions**: Use search_course_content first, fall back to search_web if needed
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
  """

    def __init__(self, api_key: str, model: str):
        self.client = groq.Groq(api_key=api_key)
        self.model = model

        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }

    def generate_response(
        self,
        query: str,
        conversation_history: str | None = None,
        tools: list | None = None,
        tool_manager=None,
    ) -> str:
        """
        Generate AI response with optional tool usage and conversation context.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools

        Returns:
            Generated response as string
        """

        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]

        api_params = {
            **self.base_params,
            "messages": messages
        }

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**api_params)
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and tool_manager:
            return self._handle_tool_execution(choice, api_params, tool_manager)

        return choice.message.content

    def _handle_tool_execution(self, choice, base_params: dict, tool_manager) -> str:
        """
        Handle execution of tool calls and get follow-up response.

        Args:
            choice: The choice containing tool use requests
            base_params: Base API parameters
            tool_manager: Manager to execute tools

        Returns:
            Final response text after tool execution
        """
        messages = base_params["messages"].copy()
        messages.append({
            "role": "assistant",
            "content": choice.message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in choice.message.tool_calls
            ]
        })

        tool_results = []
        for tc in choice.message.tool_calls:
            tool_result = tool_manager.execute_tool(
                tc.function.name,
                **eval(tc.function.arguments)
            )

            tool_results.append({
                "tool_call_id": tc.id,
                "role": "tool",
                "content": tool_result
            })

        messages.extend(tool_results)

        final_params = {
            **self.base_params,
            "messages": messages
        }

        final_response = self.client.chat.completions.create(**final_params)
        return final_response.choices[0].message.content
