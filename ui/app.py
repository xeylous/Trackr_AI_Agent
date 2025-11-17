import gradio as gr
from main import Orchestrator

orch = Orchestrator()
user_id = None

def chat(message, email):
    global user_id
    if not user_id and email:
        user_id = email.lower().strip()

    response = orch.handle(user_id, message)
    return response.get("display", response)

ui = gr.ChatInterface(
    fn=chat,
    additional_inputs=gr.Textbox(label="Email for login"),
    title="🌿 LifeBalance AI",
    description="Your personalized wellness assistant."
)

def launch():
    ui.launch()

def as_text(self, response):
    """Convert agent structured output → natural UI text."""
    if "message" in response:
        return add_warmth(response["message"])

    if "data" in response:
        return add_warmth(str(response["data"]))

    return "✨ Something went wrong, try again!"

if __name__ == "__main__":
    mode = input("Run mode: CLI or Web? ").strip().lower()

    if mode == "web":
        from ui.app import launch
        launch()
    else:
        main()

