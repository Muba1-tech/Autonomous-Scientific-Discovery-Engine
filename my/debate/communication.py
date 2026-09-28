class MessageBus:
    def __init__(self):
        self.history = []
        
    def broadcast(self, agent_name, message):
        self.history.append({"agent": agent_name, "message": message})
        
    def get_transcript(self):
        return "\n".join([f"[{msg['agent']}]: {msg['message']}" for msg in self.history])
