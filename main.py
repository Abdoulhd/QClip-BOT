import os
from bot import main

if __name__ == "__main__":
    # Set the port for Railway deployment
    port = int(os.environ.get("PORT", 8080))
    
    # Run the bot
    main()