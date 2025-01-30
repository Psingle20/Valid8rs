FROM python:3.10-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies directly using pip
RUN pip install --no-cache-dir --verbose fastapi uvicorn python-dotenv pydantic pydantic-settings tweepy groq beautifulsoup4 wikipedia duckduckgo-search langgraph python-multipart httpx requests

# Expose port (use the port you want to run the app on)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$port", "--reload"]
