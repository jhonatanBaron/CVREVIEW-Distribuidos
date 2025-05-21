import pika
import json
import os
import time
from openai import OpenAI
# Check for OpenAI API key
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Configuración de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# Conexión a RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        break
    except Exception as e:
        print("Esperando RabbitMQ...", e)
        time.sleep(5)

channel = connection.channel()
channel.queue_declare(queue="analysis_queue", durable=True)
channel.queue_declare(queue="evaluation_queue", durable=True)

def evaluate_cv_with_ai(tech_analysis):
    # Preparar los datos para el prompt
    skills_data = {
        'programming': tech_analysis.get('programming_languages', []),
        'frameworks': tech_analysis.get('frameworks', []),
        'databases': tech_analysis.get('databases', []),
        'cloud': tech_analysis.get('cloud_platforms', []),
        'tools': tech_analysis.get('development_tools', []),
        'soft_skills': tech_analysis.get('soft_skills', [])
    }

    prompt = f"""
    As a tech career advisor, evaluate this CV based on the following skills:
    
    Technical Skills Found:
    - Programming Languages: {', '.join(skills_data['programming'])}
    - Frameworks: {', '.join(skills_data['frameworks'])}
    - Databases: {', '.join(skills_data['databases'])}
    - Cloud & DevOps: {', '.join(skills_data['cloud'])}
    - Development Tools: {', '.join(skills_data['tools'])}
    - Soft Skills: {', '.join(skills_data['soft_skills'])}

    Please provide:
    1. Overall CV score (0-100)
    2. Strengths analysis
    3. Areas for improvement
    4. Specific recommendations for skill development
    
    Return the response in JSON format with the following structure:
    {
        "score": number,
        "strengths": [list of strings],
        "areas_for_improvement": [list of strings],
        "skill_development_recommendations": [list of strings]
    }
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert tech career advisor with deep knowledge of the software industry."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error en la evaluación de IA: {e}")
        return None

def callback(ch, method, properties, body):
    data = json.loads(body)
    cv_id = data["cv_id"]
    tech_analysis = data["tech_analysis"]

    print(f"Evaluando CV ID: {cv_id}")

    try:
        # Obtener evaluación de la IA
        cv_evaluation = evaluate_cv_with_ai(tech_analysis)
        
        if cv_evaluation:
            result = {
                "cv_id": cv_id,
                "evaluation": cv_evaluation,
                "raw_analysis": tech_analysis
            }

            channel.basic_publish(
                exchange="",
                routing_key="evaluation_queue",
                body=json.dumps(result),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            print(f"Evaluación completada para CV ID: {cv_id}")
        
    except Exception as e:
        print(f"Error en el proceso de evaluación: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="analysis_queue", on_message_callback=callback)

print("CVEvaluatorWorker escuchando analysis_queue...")
channel.start_consuming()