import pika
import json
import os
import time
import spacy

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# Cargar modelo de spaCy
nlp = spacy.load("en_core_web_sm")

# Reintento de conexión a RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        break
    except Exception as e:
        print("Esperando RabbitMQ...", e)
        time.sleep(5)

channel = connection.channel()
channel.queue_declare(queue="keyword_queue", durable=True)
channel.queue_declare(queue="analysis_queue", durable=True)

def is_probably_english(text: str) -> bool:
    # Lista básica de palabras comunes en español
    spanish_words = {'de', 'la', 'el', 'en', 'con', 'para', 'por', 'los', 'las'}
    
    # Tomar las primeras 50 palabras del texto
    words = set(text.lower().split()[:50])
    
    # Si hay muchas palabras en español, probablemente no es inglés
    spanish_count = len(words.intersection(spanish_words))
    return spanish_count < 3


def extract_keywords(text: str):
    doc = nlp(text)
    
    tech_info = {
        'programming_languages': set(),
        'frameworks': set(),
        'databases': set(),
        'cloud_platforms': set(),
        'development_tools': set(),
        'soft_skills': set(),
        'job_roles': set(),
        'education': set()
    }

    # Diccionarios de tecnologías específicas
    tech_keywords = {
        'programming_languages': {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 
            'rust', 'swift', 'kotlin'
        },
        'frameworks': {
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express',
            'laravel', '.net', 'fastapi', 'bootstrap'
        },
        'databases': {
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'elasticsearch',
            'cassandra', 'dynamodb'
        },
        'cloud_platforms': {
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'gitlab', 'github'
        },
        'development_tools': {
            'git', 'jira', 'vscode', 'intellij', 'postman', 'swagger', 'linux', 'agile',
            'scrum', 'ci/cd'
        }
    }

    tech_roles = {
        'backend developer', 'frontend developer', 'full stack developer', 
        'devops engineer', 'software engineer', 'data engineer', 'cloud architect',
        'system administrator', 'technical lead', 'software architect'
    }

    tech_soft_skills = {
        'problem solving', 'teamwork', 'agile methodology', 'communication',
        'code review', 'mentoring', 'technical documentation'
    }

    # Analizar el texto
    for sent in doc.sents:
        sent_text = sent.text.lower()
        
        # Detectar tecnologías
        for category, terms in tech_keywords.items():
            found_terms = {term for term in terms if term in sent_text}
            tech_info[category].update(found_terms)
        
        # Detectar roles
        for role in tech_roles:
            if role in sent_text:
                tech_info['job_roles'].add(role)
        
        # Detectar soft skills
        for skill in tech_soft_skills:
            if skill in sent_text:
                tech_info['soft_skills'].add(skill)

    # Detectar educación relacionada con IT
    for ent in doc.ents:
        if ent.label_ == "ORG":
            if any(edu_term in ent.text.lower() for edu_term in 
                  ['computer science', 'engineering', 'information technology']):
                tech_info['education'].add(ent.text.strip())

    # Generar recomendaciones de roles
    recommendations = get_tech_job_recommendations(tech_info)

    return {
        'analysis': {
            category: list(items) 
            for category, items in tech_info.items() 
            if items
        },
        'recommendations': recommendations
    }
def get_tech_job_recommendations(tech_info):
    role_requirements = {
        'backend developer': {
            'required_languages': {'python', 'java', 'c#'},
            'required_databases': {'postgresql', 'mysql', 'mongodb'},
            'preferred_tools': {'git', 'docker'}
        },
        'frontend developer': {
            'required_languages': {'javascript', 'typescript'},
            'required_frameworks': {'react', 'angular', 'vue'},
            'preferred_tools': {'git', 'webpack'}
        },
        'devops engineer': {
            'required_tools': {'docker', 'kubernetes', 'jenkins', 'terraform'},
            'required_platforms': {'aws', 'azure', 'gcp'},
            'preferred_languages': {'python', 'bash'}
        }
    }

    matches = []
    programming_languages = tech_info['programming_languages']
    frameworks = tech_info['frameworks']
    tools = tech_info['development_tools']
    
    for role, requirements in role_requirements.items():
        score = 0
        if programming_languages & requirements.get('required_languages', set()):
            score += 2
        if frameworks & requirements.get('required_frameworks', set()):
            score += 2
        if tools & requirements.get('required_tools', set()):
            score += 1
            
        if score >= 3:
            matches.append({
                'role': role,
                'match_score': score
            })
    
    # Ordenar por puntuación
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:3]  # Retornar los 3 mejores matches

# Callback de RabbitMQ
def callback(ch, method, properties, body):
    data = json.loads(body)
    cv_id = data["cv_id"]
    text = data["text"]

    print(f"Procesando CV tech ID: {cv_id}")

    try:
        if not is_probably_english(text):
            raise ValueError("El CV debe estar en inglés")

        analysis_result = extract_keywords(text)
        result = {
            "cv_id": cv_id,
            "tech_analysis": analysis_result['analysis'],
            "job_recommendations": analysis_result['recommendations']
        }

        channel.basic_publish(
            exchange="",
            routing_key="analysis_queue",
            body=json.dumps(result),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print(f"Análisis tech enviado a analysis_queue (CV ID: {cv_id})")

    except Exception as e:
        print(f"Error procesando texto: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="keyword_queue", on_message_callback=callback)

print("KeywordWorker escuchando keyword_queue...")
channel.start_consuming()
