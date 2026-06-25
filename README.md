# maya-td-bot
Transitioning from Rotomation to Programming over the past year has been an incredible journey. Today, I’m excited to share a personal project I’ve been developing to bridge the gap between AI and 3D pipelines: The Maya TD Bot. 🚀🐍
As someone who works closely with Autodesk Maya, I wanted an AI assistant that doesn’t just generate generic Python scripts, but actually understands the strict constraints of a production environment.

I built this tool using the Gemini API, focusing on making it a practical, production-ready assistant. Here are some of the technical highlights under the hood:

🔹 Cross-Version UI Compatibility: Dynamically handles PySide2 and PySide6, ensuring the tool works seamlessly from Maya 2020 all the way to 2025.
🔹 Context-Aware Injection & Guardrails: I implemented strict token rules. For example, the bot is restricted from using cmds.hyperShade or hardcoding joint names, ensuring it strictly follows clean Rigging and Arnold rendering standards.
🔹 Dual Execution Modes:

[Quick Action] for executing direct commands in memory without cluttering the script editor.

[Save Script] for generating formal tools, which it automatically saves to the Maya scripts directory and opens a command port (7001) ready for VS Code debugging.
🔹 Background Threading: Utilizing QThread so Maya's UI doesn't freeze while waiting for the API response.
