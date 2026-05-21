from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP
mcp = FastMCP("Backlog")

BACKLOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backlog.md"))

@mcp.tool()
def get_backlog() -> str:
    """Reads the current contents of the Backlog.md file."""
    if not os.path.exists(BACKLOG_PATH):
        return "Error: Backlog.md not found."
    with open(BACKLOG_PATH, "r") as f:
        return f.read()

@mcp.tool()
def add_developer_note(ticket_id: str, note: str) -> str:
    """Appends a developer note to a specific ticket in Backlog.md."""
    if not os.path.exists(BACKLOG_PATH):
        return "Error: Backlog.md not found."
    
    with open(BACKLOG_PATH, "r") as f:
        lines = f.readlines()
        
    updated_lines = []
    ticket_found = False
    in_target_ticket = False
    
    for line in lines:
        if line.startswith("## Ticket") and ticket_id in line:
            ticket_found = True
            in_target_ticket = True
            updated_lines.append(line)
        elif line.startswith("## Ticket") and in_target_ticket:
            # Reached the next ticket, insert note before it
            updated_lines.append(f"**Developer Note:** {note}\n\n")
            in_target_ticket = False
            updated_lines.append(line)
        else:
            updated_lines.append(line)
            
    if ticket_found and in_target_ticket:
        # If it was the last ticket, append at the end
        updated_lines.append(f"**Developer Note:** {note}\n\n")
        
    if not ticket_found:
        return f"Error: Ticket {ticket_id} not found."
        
    with open(BACKLOG_PATH, "w") as f:
        f.writelines(updated_lines)
        
    return f"Successfully added note to Ticket {ticket_id}."

if __name__ == "__main__":
    mcp.run()
