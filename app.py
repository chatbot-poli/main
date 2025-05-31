from flask import Flask, request, jsonify, session, render_template
import cohere
import os
#qB6xcaI2z1YpQoy9N21l0bl8RJYKxVGebOtjYbg6

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración de Cohere
api_key = os.getenv("COHERE_API_KEY")  # Usa variable de entorno
client = cohere.Client(api_key)

chat_history = [{
    "role": "System",
    "message": (
        "Eres un chatbot programable y experto en múltiples áreas académicas y profesionales, diseñado para responder con precisión y MUCHA BREVEDAD. "
        "Respondes consultas relacionadas con:\n"
        "- Cálculo de salarios y funciones contables en Paraguay.\n"
        "- Funciones del área de Gestión del Talento Humano (GTH) en empresas.\n"
        "- Auditoría interna, externa, administrativa y social.\n"
        "- Tipos de liderazgo y teorías administrativas (como Teoría X/Y, Likert, malla de Blake y Mouton, enfoque situacional, etc.).\n"
        "- Concepto de calidad en empresas y metodologías como Just In Time, Reingeniería, y Calidad Total.\n"
        "- Distribución de aportes al IPS y beneficios del seguro social.\n"
        "Tus respuestas deben ser MUY BREVES, claras y centradas en lo que se te pregunta. Evita rodeos innecesarios, a menos que se solicite más detalle. "
        "Tus respuestas deben ser BREVES y resumidas"
    )
}]


frases_sueldo = [
    "calcular mi sueldo", "calcula mi sueldo", "quiero calcular mi sueldo",
    "calcular salario", "calcula mi salario", "quiero calcular mi salario", "me podrias calcular mi salario",
    "cómo calcular mi sueldo", "cuanto gano", "quiero saber mi sueldo",
    "cálculo de salario", "calcular pago", "cuanto cobrare", 
    "cuánto voy a ganar", "calcular sueldo", "calcules mi salario", "calculas mi salario"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json["message"].strip().lower()

    if 'estado' not in session:
        session['estado'] = 'saludo'

    if session['estado'] == 'saludo':
        if any(frase in user_input for frase in frases_sueldo):
            session['estado'] = 'calcular_salario'
            return jsonify({'response': "Ingresa el tipo de contrato (dependiente/independiente)."})

    if session['estado'] == 'calcular_salario':
        if user_input == 'dependiente':
            session['estado'] = 'salario_dependiente'
            return jsonify({'response': "Ingresa tu salario por favor (solo números en guaraníes)."})
        elif user_input == 'independiente':
            session['estado'] = 'salario_independiente'
            return jsonify({'response': "Ingresa tu salario por favor (solo números en guaraníes)."})
        else:
            return jsonify({'response': "Solo acepto 'dependiente' o 'independiente' como respuestas."})

    if session['estado'] == 'salario_dependiente':
        try:
            salario = float(user_input)
            if salario >= 2798309:
                ips_descuento = salario * 0.09
                salario_neto = salario - ips_descuento
                session['estado'] = 'saludo'
                return jsonify({
                    'response': f"Tu salario bruto es: {salario} Gs\n"
                                f"Descuento por IPS: {ips_descuento} Gs\n"
                                f"Tu salario neto es: {salario_neto} Gs\n"
                                "¿Te gustaría hacer otra consulta?"
                })
            else:
                return jsonify({'response': "El salario ingresado es menor al salario mínimo vigente, por favor ingresar un salario válido."})
        except ValueError:
            return jsonify({'response': "Por favor, ingresa un número válido para tu salario."})

    if session['estado'] == 'salario_independiente':
        try:
            salario = float(user_input)
            session['salario'] = salario
            session['estado'] = 'preguntar_ips'
            return jsonify({'response': "¿Quieres asociarte al seguro de IPS? (responde con 'si' o 'no')"})
        except ValueError:
            return jsonify({'response': "Por favor, ingresa un número válido para tu salario."})

    if session['estado'] == 'preguntar_ips':
        salario = session.get('salario', 0)
        if salario == 0:
            return jsonify({'response': "Parece que hubo un error al recuperar tu salario."})

        if user_input == 'si':
            ips_descuento = salario * 0.13
            iva = salario * 0.10
            salario_neto = salario - ips_descuento - iva
            session['estado'] = 'saludo'
            return jsonify({
                'response': f"Tu salario bruto es: {salario} Gs\n"
                            f"Descuento por IPS: {ips_descuento} Gs\n"
                            f"Descuento por IVA: {iva} Gs\n"
                            f"Tu salario neto es: {salario_neto} Gs\n"
                            "¿Te gustaría hacer otra consulta?"
            })
        elif user_input == 'no':
            iva = salario * 0.10
            salario_neto = salario - iva
            session['estado'] = 'saludo'
            return jsonify({
                'response': f"Tu salario bruto es: {salario} Gs\n"
                            f"Descuento por IVA: {iva} Gs\n"
                            f"Tu salario neto es: {salario_neto} Gs\n"
                            "¿Te gustaría hacer otra consulta?"
            })
        else:
            return jsonify({'response': "Por favor, responde con 'sí' o 'no'."})

    else:
        session['estado'] = 'saludo'
        chat_history.append({"role": "User", "message": user_input})

        response = client.chat(
            model="command-r",
            message=user_input,
            chat_history=chat_history
        )

        chat_history.append({"role": "Chatbot", "message": response.text})
        return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run()
