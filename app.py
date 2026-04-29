import streamlit as st
import math

st.set_page_config(page_title="By Norja - Nail Price Coach", page_icon="💅")

# ===============================
# 🌍 IDIOMA / LANGUAGE
# ===============================

language = st.session_state.get("language", "Español")

TEXT = {
    "Español": {
        "title": "💅 By Norja - Nail Price Coach",
        "subtitle": "Calcula si tus precios cubren materiales, tiempo, desplazamientos y gastos reales.",
        "currency_select": "🌍 Elige la moneda",
        "pro_access": "🔒 Acceso PRO",
        "mode_question": "¿Cómo quieres calcular?",
        "quick_mode": "💗 Rápido",
        "pro_mode": "💎 Pro",
        "select_option": "Selecciona una opción",
        "no_extra_time": "No cuento tiempo extra",
        "quick_header": "Cálculo rápido",
        "quick_info": "Modo rápido: cálculo general usando promedios. Ideal si quieres una orientación sin meter cada servicio por separado.",
        "avg_price": "¿Cuánto cobras en promedio por clienta?",
        "clients_month": "¿Cuántas clientas atiendes al mes?",
        "avg_time": "¿Cuánto tardas en promedio por clienta?",
        "desired_hour": "¿Qué referencia quieres usar para valorar tu tiempo?",
        "desired_hour_help": "Si estás empezando y no sabes qué poner, prueba varios escenarios: 5, 8, 10, 12 y 15 por hora.",
        "materials_month": "¿Cuánto gastas en materiales al mes?",
        "materials_help": "Incluye gel, tips, limas, algodón, alcohol, cleanser, guantes, decoración, packaging, etc.",
        "other_expenses": "Otros gastos mensuales del negocio",
        "other_expenses_help": "Ejemplo: luz, internet, publicidad, cursos, apps, teléfono, limpieza, reposición general, etc.",
        "where_work_header": "Dónde trabajas",
        "where_work": "¿Dónde trabajas?",
        "home": "Casa",
        "mobile": "Domicilio",
        "salon_commission": "Salón con comisión",
        "salon_rent": "Salón alquilando silla/mesa",
        "own_place": "Local propio",
        "commission_percent": "¿Qué porcentaje se queda el salón? (%)",
        "rent_question": "¿Cuánto pagas al mes por alquiler/silla/local?",
        "mobile_cost_header": "Coste de trabajar a domicilio",
        "travel_month": "¿Cuánto gastas al mes en gasolina/transporte/desplazamiento?",
        "travel_month_help": "Pon 0 si vas caminando o no tienes gasto. Incluye gasolina, parking, bus, taxi o transporte.",
        "travel_month_help_short": "Pon 0 si vas caminando o no tienes gasto. Incluye gasolina, parking o transporte.",
        "travel_time_client": "¿Cuánto tiempo extra pierdes por desplazamiento por clienta?",
        "travel_time_service": "¿Cuánto tiempo extra pierdes por desplazamiento por servicio?",
        "calculate_quick": "Calcular rápido",
        "warn_price": "Introduce cuánto cobras en promedio por clienta.",
        "warn_clients": "Introduce cuántas clientas atiendes al mes.",
        "warn_time": "Selecciona cuánto tardas en promedio por clienta.",
        "warn_desired_hour": "Introduce la referencia que quieres usar para valorar tu tiempo.",
        "warn_place": "Selecciona dónde trabajas.",
        "warn_travel_time_client": "Selecciona el tiempo extra de desplazamiento por clienta.",
        "warn_travel_time_service": "Selecciona el tiempo extra de desplazamiento por servicio.",
        "quick_result": "📊 Resultado rápido",
        "income_month": "💰 **Ingreso mensual:**",
        "materials_month_result": "🧴 **Materiales del mes:**",
        "other_expenses_result": "🏠 **Otros gastos:**",
        "rent_result": "🏢 **Alquiler/silla/local:**",
        "travel_result": "🚗 **Desplazamiento mensual:**",
        "commission_result": "💸 **Comisión del salón:**",
        "total_costs": "💸 **Gastos totales:**",
        "real_profit": "✅ **Ganancia real:**",
        "hours_month": "⏱️ **Horas trabajadas al mes:**",
        "hours": "horas",
        "profit_hour": "💵 **Ganancia real por hora:**",
        "recommended_avg_price": "💡 Precio recomendado promedio",
        "material_per_client": "Material promedio por clienta:",
        "fixed_per_client": "Gasto promedio por clienta:",
        "extra_travel_per_client": "Tiempo extra de desplazamiento por clienta:",
        "time_value_client": "Valor de tu tiempo por clienta:",
        "commission_adjustment": "Ajuste por comisión del salón:",
        "min_sustainable": "🔹 Precio mínimo sostenible:",
        "ideal_recommended": "🔸 Precio ideal recomendado:",
        "premium_guide": "💎 Precio premium orientativo:",
        "range_caption": "Mínimo = cubre materiales, gastos y tu tiempo. Ideal = margen más sano. Premium = rango orientativo para servicios mejor presentados o más personalizados.",
        "market_info": "Este cálculo no representa el precio de mercado de tu zona. Representa el precio que necesitarías cobrar para cubrir materiales, gastos y el valor de tu tiempo. Si el resultado parece alto para tu zona, revisa tres cosas: tiempo de trabajo, gastos y posicionamiento del servicio.",
        "market_caption": "Los precios del mercado cambian según ciudad, país y tipo de clienta. Por eso esta herramienta no adivina precios locales: calcula si tus propios números son sostenibles.",
        "current_covers": "Tu precio actual cubre el mínimo calculado. No significa que debas bajarlo.",
        "below_minimum": "Tu precio actual está por debajo del mínimo sostenible. Podrías subir al menos a",
        "simple_interpretation": "🧠 Interpretación simple",
        "losing_money_simple": "Estás perdiendo dinero. No es solo que cobres poco: tus ingresos no alcanzan para cubrir todos los gastos que metiste.",
        "below_hour_simple": "Tu precio puede cubrir gastos, pero no está pagando tu tiempo al nivel que elegiste. No estás necesariamente en pérdida, pero sí estás trabajando por menos de lo que quieres.",
        "good_numbers_simple": "Tus números tienen sentido: cubres gastos y tu ganancia por hora llega a la referencia que elegiste.",
        "home_info": "En casa no estás metiendo desplazamiento ni comisión, por eso suele salir más bajo.",
        "mobile_info": "A domicilio debe salir diferente a casa porque sumas desplazamiento mensual y/o tiempo extra.",
        "commission_info": "Como pagas comisión, el precio recomendado sube porque una parte de lo que cobras no se queda contigo.",
        "chair_info": "El alquiler de silla/mesa se reparte entre tus clientas. Si tienes pocas clientas, cada una carga más gasto.",
        "own_place_info": "El local propio puede subir mucho el precio recomendado si todavía tienes pocas clientas al mes.",
        "pro_locked": "🔒 Esta función es PRO. Introduce tu código de acceso.",
        "pro_buy_info": "Compra el acceso PRO en el link de mi perfil y recibirás el código automáticamente. Con PRO puedes analizar cada servicio, ver el resultado global y detectar qué servicio puede estar bajando tu rentabilidad.",
        "services_month": "Servicios del mes",
        "pro_info": "Modo Pro: análisis detallado por cada servicio + resultado global del negocio. Aquí podrás ver qué servicio funciona mejor y cuál está bajando tu rentabilidad.",
        "service": "Servicio",
        "service_name": "Nombre del servicio",
        "service_placeholder": "Ejemplo: Soft gel básico, Relleno, Acrílico con diseño",
        "service_price": "¿Cuánto cobras por este servicio?",
        "service_time": "¿Cuánto tardas aproximadamente en hacer este servicio?",
        "service_material": "Material que gastas en ESTE servicio por cada clienta",
        "service_material_help": "Incluye gel, tips, limas, algodón, alcohol, decoración, packaging, etc.",
        "service_qty": "¿Cuántas veces haces este servicio al mes?",
        "delete_service": "❌ Eliminar este servicio",
        "add_service": "➕ Añadir servicio",
        "business_expenses_header": "Gastos del negocio",
        "tools_question": "Herramientas o equipos que quieres recuperar",
        "tools_help": "Ejemplo: torno, lámpara, brocas, mesa, silla, aspirador, esterilizador. NO incluyas productos que se gastan en cada servicio.",
        "months_question": "¿En cuántos meses quieres recuperar esa inversión?",
        "calculate_business": "Calcular mi negocio",
        "warn_tools_months": "Selecciona en cuántos meses quieres recuperar la inversión en herramientas.",
        "warn_incomplete_price": "Hay un servicio con datos incompletos: falta el precio.",
        "warn_incomplete_time": "Hay un servicio con datos incompletos: falta el tiempo.",
        "warn_incomplete_qty": "Hay un servicio con datos incompletos: falta cuántas veces lo haces al mes.",
        "warn_valid_service": "Añade al menos un servicio válido.",
        "unnamed_service": "Servicio sin nombre",
        "analysis_service": "📌 Análisis por servicio",
        "current_price": "Precio actual:",
        "times_month": "Veces al mes:",
        "material_service": "Material por servicio:",
        "total_time_service": "Tiempo total contado por servicio:",
        "assigned_expense": "Gasto del negocio asignado por servicio:",
        "time_value_service": "Valor de tu tiempo en este servicio:",
        "profit_before_time": "Ganancia antes de valorar tu tiempo:",
        "profit_hour_service": "Ganancia aproximada por hora en este servicio:",
        "service_under_min": "🔴 Este servicio está por debajo del mínimo sostenible. Para cubrir materiales, gastos y tu tiempo, debería estar al menos en",
        "service_yellow": "🟡 Este servicio cubre el mínimo, pero deja poco margen. No está necesariamente mal, pero puede estar frenando tu ganancia.",
        "service_green": "🟢 Este servicio está bien posicionado o por encima del mínimo recomendado.",
        "global_result": "📊 Resultado global del negocio",
        "total_income_month": "💰 **Ingresos totales del mes:**",
        "materials_used": "🧴 **Materiales usados:**",
        "business_expenses_result": "🏠 **Gastos del negocio:**",
        "real_profit_approx": "✅ **Ganancia real aproximada:**",
        "global_interpretation": "🧠 Interpretación global",
        "global_loss": "🔴 Tu negocio está en pérdida. Estás gastando más de lo que ingresas. Antes de crecer, necesitas revisar precios, gastos o servicios.",
        "global_yellow": "🟡 Tu negocio deja ganancia, pero no estás alcanzando la referencia por hora que elegiste. Esto significa que no necesariamente estás perdiendo dinero, pero sí podrías estar cobrando poco para el tiempo que inviertes.",
        "global_green": "🟢 Tu negocio es rentable y estás alcanzando tu referencia por hora. Tus precios tienen una estructura más sana.",
        "worst_header": "🚨 Servicio que más puede estar afectando tu rentabilidad",
        "worst_text": "El servicio que más puede estar bajando tu rentabilidad es:",
        "minimum_recommended": "Precio mínimo recomendado:",
        "gap_minimum": "Diferencia frente al mínimo:",
        "monthly_impact": "Impacto mensual aproximado:",
        "worst_red": "Este servicio está por debajo del mínimo. Deberías revisar este primero antes de subir todos tus precios.",
        "worst_yellow": "Este servicio no está necesariamente en pérdida, pero paga peor tu tiempo que otros servicios.",
        "worst_green": "No hay un servicio claramente ruinoso, pero este es el que deja menos margen comparado con los demás.",
        "practical_recommendation": "✅ Recomendación práctica",
        "review_first": "Servicios que deberías revisar primero:",
        "red_info": "No tienes que subir todo de golpe. Empieza por los servicios rojos, porque son los que más sentido tiene corregir primero.",
        "yellow_review": "Servicios que cubren el mínimo, pero podrían mejorar margen:",
        "yellow_info": "Estos servicios no están mal, pero si quieres ganar mejor por hora, puedes ajustar algunos poco a poco.",
        "all_good": "Tus servicios están bien estructurados según los datos que introdujiste. Puedes enfocarte en mejorar presentación, fotos, packs, diseños premium o conseguir más clientas.",
        "rent_info": "El alquiler/silla/local se reparte entre todos tus servicios. Si haces pocos servicios al mes, cada servicio carga más gasto.",
        "salon_commission_info": "La comisión del salón reduce lo que realmente te queda de cada servicio.",
        "tools_month_info": "Estás repartiendo tu inversión en herramientas como",
        "final_caption": "Este cálculo no pretende decirte el precio exacto del mercado. Sirve para saber si tus precios cubren materiales, gastos y el valor de tu tiempo.",
        "final_market_info": "Este cálculo no representa el precio de mercado de tu zona. Representa el precio que necesitarías cobrar para cubrir materiales, gastos y el valor de tu tiempo. Si los precios recomendados parecen altos, no significa que estén mal: significa que el mercado y tu rentabilidad no siempre coinciden.",
        "diagnosis_no_hour": "Completa tu objetivo por hora para analizar mejor.",
        "diagnosis_loss": "🔴 Estás en pérdida: después de gastos, no queda ganancia real.",
        "diagnosis_low": "🔴 Cubres gastos parcialmente, pero tu ganancia por hora es muy baja.",
        "diagnosis_under_goal": "🟡 Cubres gastos, pero todavía no llegas a lo que quieres ganar por hora.",
        "diagnosis_good": "🟢 Tus precios cubren gastos y alcanzan tu objetivo por hora.",
        "hour_low": "Estás usando una referencia baja. Puede servir para empezar, pero no debería ser tu objetivo final.",
        "hour_prudent": "Es una referencia prudente para empezar, pero revisa si realmente compensa tu tiempo.",
        "hour_sustainable": "Es una referencia más sostenible si quieres que el trabajo tenga sentido como negocio.",
        "hour_premium": "Estás usando una referencia más profesional/premium. El precio debe acompañarse con buen acabado, fotos, atención y presentación.",
    },
    "English": {
        "title": "💅 By Norja - Nail Price Coach",
        "subtitle": "Calculate whether your prices cover materials, time, travel, and real business expenses.",
        "currency_select": "🌍 Choose currency",
        "pro_access": "🔒 PRO Access",
        "mode_question": "How do you want to calculate?",
        "quick_mode": "💗 Quick",
        "pro_mode": "💎 Pro",
        "select_option": "Select an option",
        "no_extra_time": "I do not count extra time",
        "quick_header": "Quick calculation",
        "quick_info": "Quick mode: general calculation using averages. Ideal if you want guidance without entering each service separately.",
        "avg_price": "How much do you charge on average per client?",
        "clients_month": "How many clients do you serve per month?",
        "avg_time": "How long do you take on average per client?",
        "desired_hour": "What hourly reference do you want to use to value your time?",
        "desired_hour_help": "If you are starting and do not know what to enter, try different scenarios: 5, 8, 10, 12, and 15 per hour.",
        "materials_month": "How much do you spend on materials per month?",
        "materials_help": "Include gel, tips, files, cotton, alcohol, cleanser, gloves, decorations, packaging, etc.",
        "other_expenses": "Other monthly business expenses",
        "other_expenses_help": "Example: electricity, internet, advertising, courses, apps, phone, cleaning, general replacements, etc.",
        "where_work_header": "Where you work",
        "where_work": "Where do you work?",
        "home": "Home",
        "mobile": "Mobile service",
        "salon_commission": "Salon with commission",
        "salon_rent": "Salon renting a chair/table",
        "own_place": "Own studio",
        "commission_percent": "What percentage does the salon keep? (%)",
        "rent_question": "How much do you pay per month for rent/chair/studio?",
        "mobile_cost_header": "Cost of mobile service work",
        "travel_month": "How much do you spend per month on gas/transport/travel?",
        "travel_month_help": "Enter 0 if you walk or have no cost. Include gas, parking, bus, taxi, or transport.",
        "travel_month_help_short": "Enter 0 if you walk or have no cost. Include gas, parking, or transport.",
        "travel_time_client": "How much extra travel time do you lose per client?",
        "travel_time_service": "How much extra travel time do you lose per service?",
        "calculate_quick": "Calculate quick",
        "warn_price": "Enter how much you charge on average per client.",
        "warn_clients": "Enter how many clients you serve per month.",
        "warn_time": "Select how long you take on average per client.",
        "warn_desired_hour": "Enter the hourly reference you want to use to value your time.",
        "warn_place": "Select where you work.",
        "warn_travel_time_client": "Select the extra travel time per client.",
        "warn_travel_time_service": "Select the extra travel time per service.",
        "quick_result": "📊 Quick result",
        "income_month": "💰 **Monthly income:**",
        "materials_month_result": "🧴 **Monthly materials:**",
        "other_expenses_result": "🏠 **Other expenses:**",
        "rent_result": "🏢 **Rent/chair/studio:**",
        "travel_result": "🚗 **Monthly travel:**",
        "commission_result": "💸 **Salon commission:**",
        "total_costs": "💸 **Total expenses:**",
        "real_profit": "✅ **Real profit:**",
        "hours_month": "⏱️ **Hours worked per month:**",
        "hours": "hours",
        "profit_hour": "💵 **Real profit per hour:**",
        "recommended_avg_price": "💡 Recommended average price",
        "material_per_client": "Average material per client:",
        "fixed_per_client": "Average expense per client:",
        "extra_travel_per_client": "Extra travel time per client:",
        "time_value_client": "Value of your time per client:",
        "commission_adjustment": "Salon commission adjustment:",
        "min_sustainable": "🔹 Minimum sustainable price:",
        "ideal_recommended": "🔸 Recommended ideal price:",
        "premium_guide": "💎 Premium guide price:",
        "range_caption": "Minimum = covers materials, expenses, and your time. Ideal = healthier margin. Premium = guide range for better-presented or more personalized services.",
        "market_info": "This calculation does not represent the market price in your area. It represents the price you would need to charge to cover materials, expenses, and the value of your time. If the result seems high for your area, review three things: work time, expenses, and service positioning.",
        "market_caption": "Market prices change depending on city, country, and type of client. That is why this tool does not guess local prices: it calculates whether your own numbers are sustainable.",
        "current_covers": "Your current price covers the calculated minimum. That does not mean you should lower it.",
        "below_minimum": "Your current price is below the sustainable minimum. You could increase it at least to",
        "simple_interpretation": "🧠 Simple interpretation",
        "losing_money_simple": "You are losing money. It is not only that you charge too little: your income does not cover all the expenses you entered.",
        "below_hour_simple": "Your price may cover expenses, but it is not paying your time at the level you chose. You are not necessarily losing money, but you are working for less than you want.",
        "good_numbers_simple": "Your numbers make sense: you cover expenses and your profit per hour reaches the reference you chose.",
        "home_info": "At home you are not adding travel or commission, so the result is usually lower.",
        "mobile_info": "Mobile service should be different from home because you add monthly travel and/or extra time.",
        "commission_info": "Because you pay commission, the recommended price increases because part of what you charge does not stay with you.",
        "chair_info": "Chair/table rent is spread across your clients. If you have few clients, each one carries more expense.",
        "own_place_info": "An own studio can increase the recommended price a lot if you still have few clients per month.",
        "pro_locked": "🔒 This feature is PRO. Enter your access code.",
        "pro_buy_info": "Buy PRO access through the link in my profile and you will receive the code automatically. With PRO you can analyze each service, see the global result, and detect which service may be lowering your profitability.",
        "services_month": "Services of the month",
        "pro_info": "Pro mode: detailed analysis by service + global business result. Here you can see which service performs better and which one is lowering your profitability.",
        "service": "Service",
        "service_name": "Service name",
        "service_placeholder": "Example: Basic soft gel, Refill, Acrylic with design",
        "service_price": "How much do you charge for this service?",
        "service_time": "How long does this service take approximately?",
        "service_material": "Material you spend on THIS service per client",
        "service_material_help": "Include gel, tips, files, cotton, alcohol, decorations, packaging, etc.",
        "service_qty": "How many times do you do this service per month?",
        "delete_service": "❌ Delete this service",
        "add_service": "➕ Add service",
        "business_expenses_header": "Business expenses",
        "tools_question": "Tools or equipment you want to recover",
        "tools_help": "Example: e-file, lamp, drill bits, table, chair, dust collector, sterilizer. Do NOT include products that are used up in each service.",
        "months_question": "In how many months do you want to recover that investment?",
        "calculate_business": "Calculate my business",
        "warn_tools_months": "Select in how many months you want to recover the investment in tools.",
        "warn_incomplete_price": "There is a service with incomplete data: price is missing.",
        "warn_incomplete_time": "There is a service with incomplete data: time is missing.",
        "warn_incomplete_qty": "There is a service with incomplete data: monthly quantity is missing.",
        "warn_valid_service": "Add at least one valid service.",
        "unnamed_service": "Unnamed service",
        "analysis_service": "📌 Service analysis",
        "current_price": "Current price:",
        "times_month": "Times per month:",
        "material_service": "Material per service:",
        "total_time_service": "Total time counted per service:",
        "assigned_expense": "Business expense assigned per service:",
        "time_value_service": "Value of your time in this service:",
        "profit_before_time": "Profit before valuing your time:",
        "profit_hour_service": "Approximate profit per hour in this service:",
        "service_under_min": "🔴 This service is below the sustainable minimum. To cover materials, expenses, and your time, it should be at least",
        "service_yellow": "🟡 This service covers the minimum, but leaves little margin. It is not necessarily bad, but it may be slowing down your profit.",
        "service_green": "🟢 This service is well positioned or above the recommended minimum.",
        "global_result": "📊 Global business result",
        "total_income_month": "💰 **Total monthly income:**",
        "materials_used": "🧴 **Materials used:**",
        "business_expenses_result": "🏠 **Business expenses:**",
        "real_profit_approx": "✅ **Approximate real profit:**",
        "global_interpretation": "🧠 Global interpretation",
        "global_loss": "🔴 Your business is losing money. You are spending more than you earn. Before growing, you need to review prices, expenses, or services.",
        "global_yellow": "🟡 Your business makes profit, but you are not reaching the hourly reference you chose. This means you are not necessarily losing money, but you may be charging too little for the time you invest.",
        "global_green": "🟢 Your business is profitable and you are reaching your hourly reference. Your prices have a healthier structure.",
        "worst_header": "🚨 Service that may be affecting your profitability the most",
        "worst_text": "The service that may be lowering your profitability the most is:",
        "minimum_recommended": "Recommended minimum price:",
        "gap_minimum": "Difference from the minimum:",
        "monthly_impact": "Approximate monthly impact:",
        "worst_red": "This service is below the minimum. You should review this one first before increasing all your prices.",
        "worst_yellow": "This service is not necessarily losing money, but it pays your time worse than other services.",
        "worst_green": "There is no clearly terrible service, but this is the one that leaves the least margin compared with the others.",
        "practical_recommendation": "✅ Practical recommendation",
        "review_first": "Services you should review first:",
        "red_info": "You do not have to increase everything at once. Start with the red services because they make the most sense to correct first.",
        "yellow_review": "Services that cover the minimum but could improve margin:",
        "yellow_info": "These services are not bad, but if you want to earn better per hour, you can adjust some of them little by little.",
        "all_good": "Your services are well structured according to the data you entered. You can focus on improving presentation, photos, packages, premium designs, or getting more clients.",
        "rent_info": "Rent/chair/studio cost is spread across all your services. If you do few services per month, each service carries more expense.",
        "salon_commission_info": "The salon commission reduces what you really keep from each service.",
        "tools_month_info": "You are spreading your tools investment as",
        "final_caption": "This calculation is not meant to tell you the exact market price. It helps you know whether your prices cover materials, expenses, and the value of your time.",
        "final_market_info": "This calculation does not represent the market price in your area. It represents the price you would need to charge to cover materials, expenses, and the value of your time. If the recommended prices seem high, it does not mean they are wrong: it means the market and your profitability do not always match.",
        "diagnosis_no_hour": "Complete your hourly goal to analyze better.",
        "diagnosis_loss": "🔴 You are losing money: after expenses, there is no real profit left.",
        "diagnosis_low": "🔴 You partially cover expenses, but your profit per hour is very low.",
        "diagnosis_under_goal": "🟡 You cover expenses, but you still do not reach what you want to earn per hour.",
        "diagnosis_good": "🟢 Your prices cover expenses and reach your hourly goal.",
        "hour_low": "You are using a low reference. It may help you start, but it should not be your final goal.",
        "hour_prudent": "This is a cautious reference to start, but check whether it really compensates your time.",
        "hour_sustainable": "This is a more sustainable reference if you want the work to make sense as a business.",
        "hour_premium": "You are using a more professional/premium reference. The price should be supported by good finish, photos, attention, and presentation.",
    }
}


def t(key):
    return TEXT[language].get(key, key)


# ===============================
# 🌍 MONEDA
# ===============================

currency_options = {
    "Euro (€)": "€",
    "Dólar ($)": "$",
    "Libra (£)": "£",
    "Peso mexicano (MXN $)": "MXN $",
    "Peso colombiano (COP $)": "COP $",
    "Peso chileno (CLP $)": "CLP $",
    "Peso dominicano (RD$)": "RD$",
}

col_language, col_currency = st.columns(2)

with col_language:
    language = st.selectbox(
        "🌍 Idioma / Language",
        ["Español", "English"],
        key="language"
    )

with col_currency:
    currency_label = st.selectbox(
        t("currency_select"),
        list(currency_options.keys()),
        key="currency"
    )

currency_symbol = currency_options[currency_label]

st.title(t("title"))
st.write(t("subtitle"))

st.divider()

# 🔒 ACCESO PRO SIMPLE
PRO_CODE = "NJA-8472"

pro_access_input = st.text_input(t("pro_access"), type="password")
is_pro_user = pro_access_input == PRO_CODE


def money(x):
    return f"{currency_symbol}{x:.2f}"


def diagnosis(profit_hour, desired_hour):
    if desired_hour <= 0:
        return t("diagnosis_no_hour")

    if profit_hour < 0:
        return t("diagnosis_loss")

    if profit_hour < desired_hour * 0.6:
        return t("diagnosis_low")

    if profit_hour < desired_hour:
        return t("diagnosis_under_goal")

    return t("diagnosis_good")


def final_price(current, calc):
    return max(current, math.ceil(calc))


def price_range(base):
    return base, base * 1.25, base * 1.50


def hourly_reference_text(hour):
    if hour <= 0:
        return ""

    if hour < 8:
        return t("hour_low")

    if hour < 12:
        return t("hour_prudent")

    if hour < 20:
        return t("hour_sustainable")

    return t("hour_premium")


def get_time_options():
    if language == "English":
        return {
            t("select_option"): 0,
            "30 minutes": 0.5,
            "45 minutes": 0.75,
            "1 hour": 1,
            "1 hour and a half": 1.5,
            "2 hours": 2,
            "2 hours and a half": 2.5,
            "3 hours": 3,
            "3 hours and a half": 3.5,
            "4 hours": 4,
            "4 hours and a half": 4.5,
            "5 hours": 5,
            "5 hours and a half": 5.5,
            "6 hours": 6,
            "More than 6 hours": 7,
        }

    return {
        t("select_option"): 0,
        "30 minutos": 0.5,
        "45 minutos": 0.75,
        "1 hora": 1,
        "1 hora y media": 1.5,
        "2 horas": 2,
        "2 horas y media": 2.5,
        "3 horas": 3,
        "3 horas y media": 3.5,
        "4 horas": 4,
        "4 horas y media": 4.5,
        "5 horas": 5,
        "5 horas y media": 5.5,
        "6 horas": 6,
        "Más de 6 horas": 7,
    }


def get_travel_time_options():
    if language == "English":
        return {
            t("select_option"): None,
            t("no_extra_time"): 0,
            "30 extra minutes": 0.5,
            "1 extra hour": 1,
            "1 extra hour and a half": 1.5,
            "2 extra hours": 2,
        }

    return {
        t("select_option"): None,
        t("no_extra_time"): 0,
        "30 minutos extra": 0.5,
        "1 hora extra": 1,
        "1 hora y media extra": 1.5,
        "2 horas extra": 2,
    }


time_options = get_time_options()
travel_time_options = get_travel_time_options()

place_options = [
    t("select_option"),
    t("home"),
    t("mobile"),
    t("salon_commission"),
    t("salon_rent"),
    t("own_place"),
]

mode = st.radio(t("mode_question"), [t("quick_mode"), t("pro_mode")], key="mode")

st.divider()

# ===============================
# 💗 MODO RÁPIDO
# ===============================

if mode == t("quick_mode"):

    st.header(t("quick_header"))
    st.info(t("quick_info"))

    price = st.number_input(
        f"{t('avg_price')} ({currency_symbol})",
        0, 500, 0, step=1, key="r_price"
    )

    clients = st.number_input(
        t("clients_month"),
        0, 300, 0, step=1, key="r_clients"
    )

    time_label = st.selectbox(
        t("avg_time"),
        list(time_options.keys()),
        key="r_time"
    )
    service_time = time_options[time_label]

    desired_hour = st.number_input(
        f"{t('desired_hour')} ({currency_symbol} por hora / per hour)",
        0, 100, 0, step=1, key="r_hour",
        help=t("desired_hour_help")
    )

    if desired_hour > 0:
        st.caption(hourly_reference_text(desired_hour))

    materials = st.number_input(
        f"{t('materials_month')} ({currency_symbol})",
        0, 5000, 0, step=5, key="r_mat",
        help=t("materials_help")
    )

    other_expenses = st.number_input(
        f"{t('other_expenses')} ({currency_symbol})",
        0, 5000, 0, step=5, key="r_exp",
        help=t("other_expenses_help")
    )

    st.subheader(t("where_work_header"))

    place = st.selectbox(
        t("where_work"),
        place_options,
        key="r_place"
    )

    rent = 0
    commission = 0
    travel_month = 0
    travel_time = 0

    if place == t("salon_commission"):
        commission = st.number_input(
            t("commission_percent"),
            0, 100, 0, step=1, key="r_comm"
        )

    if place in [t("salon_rent"), t("own_place")]:
        rent = st.number_input(
            f"{t('rent_question')} ({currency_symbol})",
            0, 10000, 0, step=10, key="r_rent"
        )

    if place == t("mobile"):
        st.subheader(t("mobile_cost_header"))

        travel_month = st.number_input(
            f"{t('travel_month')} ({currency_symbol})",
            0, 2000, 0, step=5, key="r_travel_month",
            help=t("travel_month_help")
        )

        travel_time_label = st.selectbox(
            t("travel_time_client"),
            list(travel_time_options.keys()),
            key="r_travel_time"
        )
        travel_time = travel_time_options[travel_time_label]

    if st.button(t("calculate_quick"), type="primary", key="r_calc"):

        if price <= 0:
            st.warning(t("warn_price"))
            st.stop()

        if clients <= 0:
            st.warning(t("warn_clients"))
            st.stop()

        if service_time <= 0:
            st.warning(t("warn_time"))
            st.stop()

        if desired_hour <= 0:
            st.warning(t("warn_desired_hour"))
            st.stop()

        if place == t("select_option"):
            st.warning(t("warn_place"))
            st.stop()

        if place == t("mobile") and travel_time is None:
            st.warning(t("warn_travel_time_client"))
            st.stop()

        income = price * clients
        commission_value = income * (commission / 100)

        non_commission_cost = materials + other_expenses + rent + travel_month
        total_cost = non_commission_cost + commission_value

        total_time_per_client = service_time + travel_time
        total_hours = clients * total_time_per_client

        profit = income - total_cost
        profit_hour = profit / total_hours if total_hours > 0 else 0

        material_per_client = materials / clients
        fixed_cost_per_client = (other_expenses + rent + travel_month) / clients
        time_value = desired_hour * total_time_per_client

        base_without_commission = material_per_client + fixed_cost_per_client + time_value

        if commission > 0 and commission < 100:
            calculated_minimum = base_without_commission / (1 - commission / 100)
        else:
            calculated_minimum = base_without_commission

        recommended = final_price(price, calculated_minimum)
        min_price, ideal_price, max_price = price_range(calculated_minimum)

        st.subheader(t("quick_result"))

        st.write(diagnosis(profit_hour, desired_hour))

        st.write(f"{t('income_month')} {money(income)}")
        st.write(f"{t('materials_month_result')} {money(materials)}")
        st.write(f"{t('other_expenses_result')} {money(other_expenses)}")

        if rent > 0:
            st.write(f"{t('rent_result')} {money(rent)}")

        if travel_month > 0:
            st.write(f"{t('travel_result')} {money(travel_month)}")

        if commission_value > 0:
            st.write(f"{t('commission_result')} {money(commission_value)}")

        st.write(f"{t('total_costs')} {money(total_cost)}")
        st.write(f"{t('real_profit')} {money(profit)}")
        st.write(f"{t('hours_month')} {total_hours:.1f} {t('hours')}")
        st.write(f"{t('profit_hour')} {money(profit_hour)}/h")

        st.divider()

        st.subheader(t("recommended_avg_price"))

        st.write(f"{t('material_per_client')} **{money(material_per_client)}**")
        st.write(f"{t('fixed_per_client')} **{money(fixed_cost_per_client)}**")

        if place == t("mobile"):
            st.write(f"{t('extra_travel_per_client')} **{travel_time:.1f} h**")

        st.write(f"{t('time_value_client')} **{money(time_value)}**")

        if commission > 0:
            st.write(f"{t('commission_adjustment')} **{commission}%**")

        st.write(f"{t('min_sustainable')} **{money(min_price)}**")
        st.write(f"{t('ideal_recommended')} **{money(ideal_price)}**")
        st.write(f"{t('premium_guide')} **{money(max_price)}**")

        st.caption(t("range_caption"))

        st.info(t("market_info"))

        st.caption(t("market_caption"))

        if calculated_minimum <= price:
            st.success(t("current_covers"))
        else:
            st.warning(
                f"{t('below_minimum')} **{money(recommended)}**."
            )

        st.divider()

        st.subheader(t("simple_interpretation"))

        if profit < 0:
            st.error(t("losing_money_simple"))
        elif profit_hour < desired_hour:
            st.warning(t("below_hour_simple"))
        else:
            st.success(t("good_numbers_simple"))

        if place == t("home"):
            st.info(t("home_info"))

        elif place == t("mobile"):
            st.info(t("mobile_info"))

        elif place == t("salon_commission"):
            st.info(t("commission_info"))

        elif place == t("salon_rent"):
            st.info(t("chair_info"))

        elif place == t("own_place"):
            st.info(t("own_place_info"))


# ===============================
# 💎 MODO PRO
# ===============================

elif mode == t("pro_mode"):

    if not is_pro_user:
        st.warning(t("pro_locked"))

        st.info(t("pro_buy_info"))

        st.stop()

    st.header(t("services_month"))
    st.info(t("pro_info"))

    if "services" not in st.session_state:
        st.session_state.services = [
            {"name": "", "price": 0, "time_label": t("select_option"), "material": 0, "qty": 0}
        ]

    def add_service():
        st.session_state.services.append(
            {"name": "", "price": 0, "time_label": t("select_option"), "material": 0, "qty": 0}
        )

    def remove_service(index):
        st.session_state.services.pop(index)

    for i, s in enumerate(st.session_state.services):

        st.subheader(f"{t('service')} {i + 1}")

        s["name"] = st.text_input(
            t("service_name"),
            value=s["name"],
            placeholder=t("service_placeholder"),
            key=f"pro_name_{i}"
        )

        s["price"] = st.number_input(
            f"{t('service_price')} ({currency_symbol})",
            0, 1000, value=s["price"], step=1, key=f"pro_price_{i}"
        )

        current_time_label = s["time_label"] if s["time_label"] in time_options else t("select_option")

        s["time_label"] = st.selectbox(
            t("service_time"),
            list(time_options.keys()),
            index=list(time_options.keys()).index(current_time_label),
            key=f"pro_time_{i}"
        )

        s["material"] = st.number_input(
            f"{t('service_material')} ({currency_symbol})",
            0, 500, value=s["material"], step=1, key=f"pro_mat_{i}",
            help=t("service_material_help")
        )

        s["qty"] = st.number_input(
            t("service_qty"),
            0, 300, value=s["qty"], step=1, key=f"pro_qty_{i}"
        )

        if len(st.session_state.services) > 1:
            if st.button(t("delete_service"), key=f"pro_delete_{i}"):
                remove_service(i)
                st.rerun()

        st.divider()

    st.button(t("add_service"), on_click=add_service, key="pro_add_service")

    st.divider()

    st.header(t("business_expenses_header"))

    desired_hour = st.number_input(
        f"{t('desired_hour')} ({currency_symbol} por hora / per hour)",
        0, 100, 0, step=1, key="pro_hour",
        help=t("desired_hour_help")
    )

    if desired_hour > 0:
        st.caption(hourly_reference_text(desired_hour))

    other_expenses = st.number_input(
        f"{t('other_expenses')} ({currency_symbol})",
        0, 20000, 0, step=5, key="pro_exp",
        help=t("other_expenses_help")
    )

    place = st.selectbox(
        t("where_work"),
        place_options,
        key="pro_place"
    )

    rent = 0
    commission = 0
    travel_month = 0
    travel_time = 0

    if place == t("salon_commission"):
        commission = st.number_input(
            t("commission_percent"),
            0, 100, 0, step=1, key="pro_comm"
        )

    if place in [t("salon_rent"), t("own_place")]:
        rent = st.number_input(
            f"{t('rent_question')} ({currency_symbol})",
            0, 20000, 0, step=10, key="pro_rent"
        )

    if place == t("mobile"):
        st.subheader(t("mobile_cost_header"))

        travel_month = st.number_input(
            f"{t('travel_month')} ({currency_symbol})",
            0, 5000, 0, step=5, key="pro_travel_month",
            help=t("travel_month_help_short")
        )

        travel_time_label = st.selectbox(
            t("travel_time_service"),
            list(travel_time_options.keys()),
            key="pro_travel_time"
        )
        travel_time = travel_time_options[travel_time_label]

    tools = st.number_input(
        f"{t('tools_question')} ({currency_symbol})",
        0, 20000, 0, step=10, key="pro_tools",
        help=t("tools_help")
    )

    months = st.selectbox(
        t("months_question"),
        [t("select_option"), 3, 6, 12, 18, 24],
        key="pro_months"
    )

    if st.button(t("calculate_business"), type="primary", key="pro_calc"):

        if desired_hour <= 0:
            st.warning(t("warn_desired_hour"))
            st.stop()

        if place == t("select_option"):
            st.warning(t("warn_place"))
            st.stop()

        if place == t("mobile") and travel_time is None:
            st.warning(t("warn_travel_time_service"))
            st.stop()

        if tools > 0 and months == t("select_option"):
            st.warning(t("warn_tools_months"))
            st.stop()

        months_value = months if isinstance(months, int) else 1
        tools_month = tools / months_value if tools > 0 else 0

        valid_services = []
        total_income = 0
        total_material = 0
        total_hours = 0
        total_qty = 0

        for s in st.session_state.services:
            service_time = time_options[s["time_label"]] if s["time_label"] in time_options else 0

            has_any_data = (
                s["price"] > 0 or
                s["qty"] > 0 or
                s["material"] > 0 or
                service_time > 0 or
                s["name"].strip() != ""
            )

            if has_any_data:
                if s["price"] <= 0:
                    st.warning(t("warn_incomplete_price"))
                    st.stop()

                if service_time <= 0:
                    st.warning(t("warn_incomplete_time"))
                    st.stop()

                if s["qty"] <= 0:
                    st.warning(t("warn_incomplete_qty"))
                    st.stop()

                total_service_time = service_time + travel_time

                income = s["price"] * s["qty"]
                material_total = s["material"] * s["qty"]
                hours_total = total_service_time * s["qty"]

                total_income += income
                total_material += material_total
                total_hours += hours_total
                total_qty += s["qty"]

                valid_services.append({
                    "name": s["name"] or t("unnamed_service"),
                    "price": s["price"],
                    "time": service_time,
                    "total_time": total_service_time,
                    "material": s["material"],
                    "qty": s["qty"],
                    "income": income,
                    "material_total": material_total,
                    "hours_total": hours_total
                })

        if total_income <= 0:
            st.warning(t("warn_valid_service"))
            st.stop()

        commission_value = total_income * (commission / 100)

        business_expenses_without_commission = other_expenses + rent + tools_month + travel_month
        business_expenses = business_expenses_without_commission + commission_value

        total_expenses = total_material + business_expenses
        profit = total_income - total_expenses
        profit_hour = profit / total_hours if total_hours > 0 else 0

        fixed_cost_per_service = business_expenses_without_commission / total_qty if total_qty > 0 else 0

        analyzed_services = []

        st.subheader(t("analysis_service"))

        for r in valid_services:

            time_value_service = desired_hour * r["total_time"]

            base_without_commission = r["material"] + fixed_cost_per_service + time_value_service

            if commission > 0 and commission < 100:
                min_service = base_without_commission / (1 - commission / 100)
            else:
                min_service = base_without_commission

            min_s, ideal_s, max_s = price_range(min_service)

            real_profit_per_service = r["price"] - r["material"] - fixed_cost_per_service

            if commission > 0:
                real_profit_per_service -= r["price"] * (commission / 100)

            real_profit_after_time = real_profit_per_service - time_value_service
            real_profit_per_hour = real_profit_per_service / r["total_time"] if r["total_time"] > 0 else 0

            gap_to_minimum = r["price"] - min_s

            analyzed_services.append({
                "name": r["name"],
                "price": r["price"],
                "qty": r["qty"],
                "min_price": min_s,
                "ideal_price": ideal_s,
                "max_price": max_s,
                "real_profit_per_service": real_profit_per_service,
                "real_profit_after_time": real_profit_after_time,
                "real_profit_per_hour": real_profit_per_hour,
                "gap_to_minimum": gap_to_minimum,
                "total_impact": real_profit_after_time * r["qty"],
                "hours_total": r["hours_total"]
            })

            st.write(f"### {r['name']}")

            st.write(f"{t('current_price')} **{money(r['price'])}**")
            st.write(f"{t('times_month')} **{int(r['qty'])}**")
            st.write(f"{t('material_service')} **{money(r['material'])}**")
            st.write(f"{t('total_time_service')} **{r['total_time']:.1f} h**")
            st.write(f"{t('assigned_expense')} **{money(fixed_cost_per_service)}**")
            st.write(f"{t('time_value_service')} **{money(time_value_service)}**")

            if commission > 0:
                st.write(f"{t('commission_adjustment')} **{commission}%**")

            st.write(f"{t('min_sustainable')} **{money(min_s)}**")
            st.write(f"{t('ideal_recommended')} **{money(ideal_s)}**")
            st.write(f"{t('premium_guide')} **{money(max_s)}**")

            st.info(t("market_info"))

            st.write(f"{t('profit_before_time')} **{money(real_profit_per_service)}**")
            st.write(f"{t('profit_hour_service')} **{money(real_profit_per_hour)}/h**")

            if r["price"] < min_s:
                st.error(
                    f"{t('service_under_min')} **{money(math.ceil(min_s))}**."
                )
            elif r["price"] < ideal_s:
                st.warning(t("service_yellow"))
            else:
                st.success(t("service_green"))

            st.divider()

        st.subheader(t("global_result"))

        st.write(diagnosis(profit_hour, desired_hour))

        st.write(f"{t('total_income_month')} {money(total_income)}")
        st.write(f"{t('materials_used')} {money(total_material)}")
        st.write(f"{t('business_expenses_result')} {money(business_expenses)}")
        st.write(f"{t('total_costs')} {money(total_expenses)}")
        st.write(f"{t('real_profit_approx')} {money(profit)}")
        st.write(f"{t('hours_month')} {total_hours:.1f} {t('hours')}")
        st.write(f"{t('profit_hour')} {money(profit_hour)}/h")

        st.divider()

        st.subheader(t("global_interpretation"))

        if profit < 0:
            st.error(t("global_loss"))

        elif profit_hour < desired_hour:
            st.warning(t("global_yellow"))

        else:
            st.success(t("global_green"))

        st.divider()

        st.subheader(t("worst_header"))

        worst_service = min(analyzed_services, key=lambda x: x["total_impact"])

        st.write(f"{t('worst_text')} **{worst_service['name']}**")

        st.write(f"{t('current_price')} **{money(worst_service['price'])}**")
        st.write(f"{t('minimum_recommended')} **{money(worst_service['min_price'])}**")
        st.write(f"{t('gap_minimum')} **{money(worst_service['gap_to_minimum'])}**")
        st.write(f"{t('monthly_impact')} **{money(worst_service['total_impact'])}**")

        if worst_service["gap_to_minimum"] < 0:
            st.error(t("worst_red"))
        elif worst_service["real_profit_per_hour"] < desired_hour:
            st.warning(t("worst_yellow"))
        else:
            st.success(t("worst_green"))

        st.divider()

        st.subheader(t("practical_recommendation"))

        red_services = [s for s in analyzed_services if s["price"] < s["min_price"]]
        yellow_services = [s for s in analyzed_services if s["price"] >= s["min_price"] and s["price"] < s["ideal_price"]]

        if red_services:
            st.write(t("review_first"))

            for s in red_services:
                st.write(
                    f"🔴 **{s['name']}** — {t('current_price')} {money(s['price'])}, "
                    f"{t('minimum_recommended')} {money(math.ceil(s['min_price']))}"
                )

            st.info(t("red_info"))

        elif yellow_services:
            st.write(t("yellow_review"))

            for s in yellow_services:
                st.write(
                    f"🟡 **{s['name']}** — {t('current_price')} {money(s['price'])}, "
                    f"{t('ideal_recommended')} {money(math.ceil(s['ideal_price']))}"
                )

            st.info(t("yellow_info"))

        else:
            st.success(t("all_good"))

        st.divider()

        if rent > 0:
            st.info(t("rent_info"))

        if commission > 0:
            st.info(t("salon_commission_info"))

        if travel_month > 0 or travel_time > 0:
            st.info(t("mobile_info"))

        if tools_month > 0:
            st.info(
                f"{t('tools_month_info')} {money(tools_month)} al mes / per month."
            )

        st.caption(t("final_caption"))

        st.info(t("final_market_info"))

        st.caption(t("market_caption"))
