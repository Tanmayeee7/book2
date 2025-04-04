from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from crewai import Agent, Task, Crew, LLM, Process

app = Flask(__name__)

# Enable CORS for all origins, allowing credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Secure NVIDIA API Key (Ensure it's set in the environment variables)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY is missing. Set it as an environment variable.")

# Initialize NVIDIA LLM
try:
    nvidia_llm = LLM(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_API_KEY
    )
except Exception as e:
    app.logger.error(f"Failed to initialize LLM: {str(e)}")
    raise RuntimeError("LLM initialization failed. Check NVIDIA API.")

@app.route('/generate-overview', methods=['POST'])
def generate_overview():
    data = request.get_json()
    topic = data.get('topic', '').strip()

    if not topic:
        return jsonify({'error': 'Book name cannot be empty!'}), 400

    try:
        # Create Agents
        searcher_agent = Agent(
            role=f"{topic} Senior Book Searcher",
            goal=f"Find and summarize the story of {topic}.",
            backstory=f"You're an expert researcher who efficiently finds structured information about {topic}.",
            llm=nvidia_llm
        )

        writer_agent = Agent(
            role=f"{topic} Book Overview Writer",
            goal=f"Write a structured and detailed overview of {topic}.",
            backstory=f"You're a skilled writer known for crafting compelling and informative overviews about {topic}.",
            llm=nvidia_llm
        )

        # Create Tasks
        search_task = Task(
            agent=searcher_agent,
            description=(
                f"Conduct thorough research on {topic}.\n"
                "Provide a structured summary in 10 bullet points.\n"
                "Include the author's name and publication year.\n"
                "Ensure chronological story order.\n"
                "No links should be included."
            ),
            expected_output=f"10 structured bullet points summarizing {topic}."
        )

        write_task = Task(
            agent=writer_agent,
            description=(
                "Expand each bullet point into a structured overview.\n"
                "Ensure clarity, accuracy, and engaging storytelling.\n"
                "Include the author's name and the year of publication.\n"
                "No links should be included."
            ),
            expected_output="A structured markdown overview without '```'."
        )

        # Create and execute Crew
        crew = Crew(
            agents=[searcher_agent, writer_agent],
            tasks=[search_task, write_task],
            verbose=True,
            process=Process.sequential  # Ensure tasks execute in order
        )

        crew_output = crew.kickoff()

        # Ensure JSON serialization safety
        overview_result = [str(output) for output in crew_output] if isinstance(crew_output, (list, tuple)) else str(crew_output)

        return jsonify({
            'success': True,
            'overview': overview_result,
            'topic': topic
        })

    except Exception as e:
        app.logger.error(f"Error generating overview: {str(e)}")
        return jsonify({'error': f'Sorry, an error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
