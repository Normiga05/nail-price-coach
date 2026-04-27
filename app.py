import streamlit as st
import math

st.set_page_config(page_title="By Norja - Nail Price Coach", page_icon="💅")

st.title("💅 By Norja - Nail Price Coach")
st.write("Calcula si tus precios cubren materiales, tiempo, desplazamientos y gastos reales.")

st.divider()

# 🔒 ACCESO PRO SIMPLE
PRO_CODE = "NJA-8472"

pro_access_input = st.text_input("🔒 Acceso PRO", type="password")
is_pro_user = pro_access_input == PRO_CODE


def money(x):
    return f"{x:.2f} €"


def diagnosis(profit_hour, desired_hour):
    if desired_hour <= 0:
        return "Completa tu objetivo por hora para analizar mejor."

    if profit_hour < 0:
        return "🔴 Estás en pérdida: después de gastos, no queda ganancia real."

    if profit_hour < desired_hour * 0.6:
        return "🔴 Cubres gastos parcialmente, pero tu ganancia por hora es muy baja."

    if profit_hour < desired_hour:
        return "🟡 Cubres gastos, pero todavía no llegas a lo que quieres ganar por hora."

    return "🟢 Tus precios cubren gastos y alcanzan tu objetivo por hora."


def final_price(current, calc):
    return max(current, math.ceil(calc))


def price_range(base):
    return base, base * 1.25, base * 1.50


def hourly_reference_text(hour):
    if hour <= 0:
        return ""

    if hour < 8:
        return "Estás usando una referencia baja. Puede servir para empezar, pero no debería ser tu objetivo final."

    if hour < 12:
        return "Es una referencia prudente para empezar, pero revisa si realmente compensa tu tiempo."

    if hour < 20:
        return "Es una referencia más sostenible si quieres que el trabajo tenga sentido como negocio."

    return "Estás usando una referencia más profesional/premium. El precio debe acompañarse con buen acabado, fotos, atención y presentación."


time_options = {
    "Selecciona una opción": 0,
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
    "Más de 6 horas": 7
}

travel_time_options = {
    "Selecciona una opción": None,
    "No cuento tiempo extra": 0,
    "30 minutos extra": 0.5,
    "1 hora extra": 1,
    "1 hora y media extra": 1.5,
    "2 horas extra": 2
}

mode = st.radio("¿Cómo quieres calcular?", ["💗 Rápido", "💎 Pro"], key="mode")

st.divider()

# ===============================
# 💗 MODO RÁPIDO
# ===============================

if mode == "💗 Rápido":

    st.header("Cálculo rápido")
    st.info(
        "Modo rápido: cálculo general usando promedios. "
        "Ideal si quieres una orientación sin meter cada servicio por separado."
    )

    price = st.number_input(
        "¿Cuánto cobras en promedio por clienta? (€)",
        0, 500, 0, step=1, key="r_price"
    )

    clients = st.number_input(
        "¿Cuántas clientas atiendes al mes?",
        0, 300, 0, step=1, key="r_clients"
    )

    time_label = st.selectbox(
        "¿Cuánto tardas en promedio por clienta?",
        list(time_options.keys()),
        key="r_time"
    )
    service_time = time_options[time_label]

    desired_hour = st.number_input(
        "¿Qué referencia quieres usar para valorar tu tiempo? (€ por hora)",
        0, 100, 0, step=1, key="r_hour",
        help="Si estás empezando y no sabes qué poner, prueba varios escenarios: 5 €, 8 €, 10 €, 12 € y 15 € por hora."
    )

    if desired_hour > 0:
        st.caption(hourly_reference_text(desired_hour))

    materials = st.number_input(
        "¿Cuánto gastas en materiales al mes? (€)",
        0, 5000, 0, step=5, key="r_mat",
        help="Incluye gel, tips, limas, algodón, alcohol, cleanser, guantes, decoración, packaging, etc."
    )

    other_expenses = st.number_input(
        "Otros gastos mensuales del negocio (€)",
        0, 5000, 0, step=5, key="r_exp",
        help="Ejemplo: luz, internet, publicidad, cursos, apps, teléfono, limpieza, reposición general, etc."
    )

    st.subheader("Dónde trabajas")

    place = st.selectbox(
        "¿Dónde trabajas?",
        ["Selecciona una opción", "Casa", "Domicilio", "Salón con comisión", "Salón alquilando silla/mesa", "Local propio"],
        key="r_place"
    )

    rent = 0
    commission = 0
    travel_month = 0
    travel_time = 0

    if place == "Salón con comisión":
        commission = st.number_input(
            "¿Qué porcentaje se queda el salón? (%)",
            0, 100, 0, step=1, key="r_comm"
        )

    if place in ["Salón alquilando silla/mesa", "Local propio"]:
        rent = st.number_input(
            "¿Cuánto pagas al mes por alquiler/silla/local? (€)",
            0, 10000, 0, step=10, key="r_rent"
        )

    if place == "Domicilio":
        st.subheader("Coste de trabajar a domicilio")

        travel_month = st.number_input(
            "¿Cuánto gastas al mes en gasolina/transporte/desplazamiento? (€)",
            0, 2000, 0, step=5, key="r_travel_month",
            help="Pon 0 si vas caminando o no tienes gasto. Incluye gasolina, parking, bus, taxi o transporte."
        )

        travel_time_label = st.selectbox(
            "¿Cuánto tiempo extra pierdes por desplazamiento por clienta?",
            list(travel_time_options.keys()),
            key="r_travel_time"
        )
        travel_time = travel_time_options[travel_time_label]

    if st.button("Calcular rápido", type="primary", key="r_calc"):

        if price <= 0:
            st.warning("Introduce cuánto cobras en promedio por clienta.")
            st.stop()

        if clients <= 0:
            st.warning("Introduce cuántas clientas atiendes al mes.")
            st.stop()

        if service_time <= 0:
            st.warning("Selecciona cuánto tardas en promedio por clienta.")
            st.stop()

        if desired_hour <= 0:
            st.warning("Introduce la referencia que quieres usar para valorar tu tiempo.")
            st.stop()

        if place == "Selecciona una opción":
            st.warning("Selecciona dónde trabajas.")
            st.stop()

        if place == "Domicilio" and travel_time is None:
            st.warning("Selecciona el tiempo extra de desplazamiento por clienta.")
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

        st.subheader("📊 Resultado rápido")

        st.write(diagnosis(profit_hour, desired_hour))

        st.write(f"💰 **Ingreso mensual:** {money(income)}")
        st.write(f"🧴 **Materiales del mes:** {money(materials)}")
        st.write(f"🏠 **Otros gastos:** {money(other_expenses)}")

        if rent > 0:
            st.write(f"🏢 **Alquiler/silla/local:** {money(rent)}")

        if travel_month > 0:
            st.write(f"🚗 **Desplazamiento mensual:** {money(travel_month)}")

        if commission_value > 0:
            st.write(f"💸 **Comisión del salón:** {money(commission_value)}")

        st.write(f"💸 **Gastos totales:** {money(total_cost)}")
        st.write(f"✅ **Ganancia real:** {money(profit)}")
        st.write(f"⏱️ **Horas trabajadas al mes:** {total_hours:.1f} horas")
        st.write(f"💵 **Ganancia real por hora:** {profit_hour:.2f} €/h")

        st.divider()

        st.subheader("💡 Precio recomendado promedio")

        st.write(f"Material promedio por clienta: **{money(material_per_client)}**")
        st.write(f"Gasto promedio por clienta: **{money(fixed_cost_per_client)}**")

        if place == "Domicilio":
            st.write(f"Tiempo extra de desplazamiento por clienta: **{travel_time:.1f} h**")

        st.write(f"Valor de tu tiempo por clienta: **{money(time_value)}**")

        if commission > 0:
            st.write(f"Ajuste por comisión del salón: **{commission}%**")

        st.write(f"🔹 Precio mínimo sostenible: **{money(min_price)}**")
        st.write(f"🔸 Precio ideal recomendado: **{money(ideal_price)}**")
        st.write(f"💎 Precio premium orientativo: **{money(max_price)}**")

        st.caption(
            "Mínimo = cubre materiales, gastos y tu tiempo. "
            "Ideal = margen más sano. Premium = rango orientativo para servicios mejor presentados o más personalizados."
        )

        st.info(
            "Este cálculo no representa el precio de mercado de tu zona. "
            "Representa el precio que necesitarías cobrar para cubrir materiales, gastos y el valor de tu tiempo. "
            "Si el resultado parece alto para tu zona, revisa tres cosas: tiempo de trabajo, gastos y posicionamiento del servicio."
        )

        st.caption(
            "Los precios del mercado cambian según ciudad, país y tipo de clienta. "
            "Por eso esta herramienta no adivina precios locales: calcula si tus propios números son sostenibles."
        )

        if calculated_minimum <= price:
            st.success("Tu precio actual cubre el mínimo calculado. No significa que debas bajarlo.")
        else:
            st.warning(
                f"Tu precio actual está por debajo del mínimo sostenible. "
                f"Podrías subir al menos a **{money(recommended)}**."
            )

        st.divider()

        st.subheader("🧠 Interpretación simple")

        if profit < 0:
            st.error(
                "Estás perdiendo dinero. No es solo que cobres poco: "
                "tus ingresos no alcanzan para cubrir todos los gastos que metiste."
            )
        elif profit_hour < desired_hour:
            st.warning(
                "Tu precio puede cubrir gastos, pero no está pagando tu tiempo al nivel que elegiste. "
                "No estás necesariamente en pérdida, pero sí estás trabajando por menos de lo que quieres."
            )
        else:
            st.success(
                "Tus números tienen sentido: cubres gastos y tu ganancia por hora llega a la referencia que elegiste."
            )

        if place == "Casa":
            st.info("En casa no estás metiendo desplazamiento ni comisión, por eso suele salir más bajo.")

        elif place == "Domicilio":
            st.info("A domicilio debe salir diferente a casa porque sumas desplazamiento mensual y/o tiempo extra.")

        elif place == "Salón con comisión":
            st.info("Como pagas comisión, el precio recomendado sube porque una parte de lo que cobras no se queda contigo.")

        elif place == "Salón alquilando silla/mesa":
            st.info("El alquiler de silla/mesa se reparte entre tus clientas. Si tienes pocas clientas, cada una carga más gasto.")

        elif place == "Local propio":
            st.info("El local propio puede subir mucho el precio recomendado si todavía tienes pocas clientas al mes.")


# ===============================
# 💎 MODO PRO
# ===============================

elif mode == "💎 Pro":

    if not is_pro_user:
        st.warning("🔒 Esta función es PRO. Introduce tu código de acceso.")

        st.info(
            "Compra el acceso PRO en el link de mi perfil y recibirás el código automáticamente. "
            "Con PRO puedes analizar cada servicio, ver el resultado global y detectar qué servicio puede estar bajando tu rentabilidad."
        )

        st.stop()

    st.header("Servicios del mes")
    st.info(
        "Modo Pro: análisis detallado por cada servicio + resultado global del negocio. "
        "Aquí podrás ver qué servicio funciona mejor y cuál está bajando tu rentabilidad."
    )

    if "services" not in st.session_state:
        st.session_state.services = [
            {"name": "", "price": 0, "time_label": "Selecciona una opción", "material": 0, "qty": 0}
        ]

    def add_service():
        st.session_state.services.append(
            {"name": "", "price": 0, "time_label": "Selecciona una opción", "material": 0, "qty": 0}
        )

    def remove_service(index):
        st.session_state.services.pop(index)

    for i, s in enumerate(st.session_state.services):

        st.subheader(f"Servicio {i + 1}")

        s["name"] = st.text_input(
            "Nombre del servicio",
            value=s["name"],
            placeholder="Ejemplo: Soft gel básico, Relleno, Acrílico con diseño",
            key=f"pro_name_{i}"
        )

        s["price"] = st.number_input(
            "¿Cuánto cobras por este servicio? (€)",
            0, 1000, value=s["price"], step=1, key=f"pro_price_{i}"
        )

        s["time_label"] = st.selectbox(
            "¿Cuánto tardas aproximadamente en hacer este servicio?",
            list(time_options.keys()),
            index=list(time_options.keys()).index(s["time_label"]) if s["time_label"] in time_options else 0,
            key=f"pro_time_{i}"
        )

        s["material"] = st.number_input(
            "Material que gastas en ESTE servicio por cada clienta (€)",
            0, 500, value=s["material"], step=1, key=f"pro_mat_{i}",
            help="Incluye gel, tips, limas, algodón, alcohol, decoración, packaging, etc."
        )

        s["qty"] = st.number_input(
            "¿Cuántas veces haces este servicio al mes?",
            0, 300, value=s["qty"], step=1, key=f"pro_qty_{i}"
        )

        if len(st.session_state.services) > 1:
            if st.button("❌ Eliminar este servicio", key=f"pro_delete_{i}"):
                remove_service(i)
                st.rerun()

        st.divider()

    st.button("➕ Añadir servicio", on_click=add_service, key="pro_add_service")

    st.divider()

    st.header("Gastos del negocio")

    desired_hour = st.number_input(
        "¿Qué referencia quieres usar para valorar tu tiempo? (€ por hora)",
        0, 100, 0, step=1, key="pro_hour",
        help="Si estás empezando y no sabes qué poner, prueba varios escenarios: 5 €, 8 €, 10 €, 12 € y 15 € por hora."
    )

    if desired_hour > 0:
        st.caption(hourly_reference_text(desired_hour))

    other_expenses = st.number_input(
        "Otros gastos mensuales del negocio (€)",
        0, 20000, 0, step=5, key="pro_exp",
        help="Ejemplo: luz, internet, publicidad, cursos, apps, teléfono, limpieza, reposición general, etc."
    )

    place = st.selectbox(
        "¿Dónde trabajas?",
        ["Selecciona una opción", "Casa", "Domicilio", "Salón con comisión", "Salón alquilando silla/mesa", "Local propio"],
        key="pro_place"
    )

    rent = 0
    commission = 0
    travel_month = 0
    travel_time = 0

    if place == "Salón con comisión":
        commission = st.number_input(
            "¿Qué porcentaje se queda el salón? (%)",
            0, 100, 0, step=1, key="pro_comm"
        )

    if place in ["Salón alquilando silla/mesa", "Local propio"]:
        rent = st.number_input(
            "¿Cuánto pagas al mes por alquiler/silla/local? (€)",
            0, 20000, 0, step=10, key="pro_rent"
        )

    if place == "Domicilio":
        st.subheader("Coste de trabajar a domicilio")

        travel_month = st.number_input(
            "¿Cuánto gastas al mes en gasolina/transporte/desplazamiento? (€)",
            0, 5000, 0, step=5, key="pro_travel_month",
            help="Pon 0 si vas caminando o no tienes gasto. Incluye gasolina, parking o transporte."
        )

        travel_time_label = st.selectbox(
            "¿Cuánto tiempo extra pierdes por desplazamiento por servicio?",
            list(travel_time_options.keys()),
            key="pro_travel_time"
        )
        travel_time = travel_time_options[travel_time_label]

    tools = st.number_input(
        "Herramientas o equipos que quieres recuperar (€)",
        0, 20000, 0, step=10, key="pro_tools",
        help="Ejemplo: torno, lámpara, brocas, mesa, silla, aspirador, esterilizador. NO incluyas productos que se gastan en cada servicio."
    )

    months = st.selectbox(
        "¿En cuántos meses quieres recuperar esa inversión?",
        ["Selecciona una opción", 3, 6, 12, 18, 24],
        key="pro_months"
    )

    if st.button("Calcular mi negocio", type="primary", key="pro_calc"):

        if desired_hour <= 0:
            st.warning("Introduce la referencia que quieres usar para valorar tu tiempo.")
            st.stop()

        if place == "Selecciona una opción":
            st.warning("Selecciona dónde trabajas.")
            st.stop()

        if place == "Domicilio" and travel_time is None:
            st.warning("Selecciona el tiempo extra de desplazamiento por servicio.")
            st.stop()

        if tools > 0 and months == "Selecciona una opción":
            st.warning("Selecciona en cuántos meses quieres recuperar la inversión en herramientas.")
            st.stop()

        months_value = months if isinstance(months, int) else 1
        tools_month = tools / months_value if tools > 0 else 0

        valid_services = []
        total_income = 0
        total_material = 0
        total_hours = 0
        total_qty = 0

        for s in st.session_state.services:
            service_time = time_options[s["time_label"]]

            has_any_data = (
                s["price"] > 0 or
                s["qty"] > 0 or
                s["material"] > 0 or
                service_time > 0 or
                s["name"].strip() != ""
            )

            if has_any_data:
                if s["price"] <= 0:
                    st.warning("Hay un servicio con datos incompletos: falta el precio.")
                    st.stop()

                if service_time <= 0:
                    st.warning("Hay un servicio con datos incompletos: falta el tiempo.")
                    st.stop()

                if s["qty"] <= 0:
                    st.warning("Hay un servicio con datos incompletos: falta cuántas veces lo haces al mes.")
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
                    "name": s["name"] or "Servicio sin nombre",
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
            st.warning("Añade al menos un servicio válido.")
            st.stop()

        commission_value = total_income * (commission / 100)

        business_expenses_without_commission = other_expenses + rent + tools_month + travel_month
        business_expenses = business_expenses_without_commission + commission_value

        total_expenses = total_material + business_expenses
        profit = total_income - total_expenses
        profit_hour = profit / total_hours if total_hours > 0 else 0

        fixed_cost_per_service = business_expenses_without_commission / total_qty if total_qty > 0 else 0

        analyzed_services = []

        st.subheader("📌 Análisis por servicio")

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

            st.write(f"Precio actual: **{money(r['price'])}**")
            st.write(f"Veces al mes: **{int(r['qty'])}**")
            st.write(f"Material por servicio: **{money(r['material'])}**")
            st.write(f"Tiempo total contado por servicio: **{r['total_time']:.1f} h**")
            st.write(f"Gasto del negocio asignado por servicio: **{money(fixed_cost_per_service)}**")
            st.write(f"Valor de tu tiempo en este servicio: **{money(time_value_service)}**")

            if commission > 0:
                st.write(f"Ajuste por comisión del salón: **{commission}%**")

            st.write(f"🔹 Precio mínimo sostenible: **{money(min_s)}**")
            st.write(f"🔸 Precio ideal recomendado: **{money(ideal_s)}**")
            st.write(f"💎 Precio premium orientativo: **{money(max_s)}**")

            st.info(
                "Este cálculo no representa el precio de mercado de tu zona. "
                "Representa el precio que necesitarías cobrar para cubrir materiales, gastos y el valor de tu tiempo. "
                "Si el resultado parece alto para tu zona, revisa tres cosas: tiempo de trabajo, gastos y posicionamiento del servicio."
            )

            st.write(f"Ganancia antes de valorar tu tiempo: **{money(real_profit_per_service)}**")
            st.write(f"Ganancia aproximada por hora en este servicio: **{real_profit_per_hour:.2f} €/h**")

            if r["price"] < min_s:
                st.error(
                    f"🔴 Este servicio está por debajo del mínimo sostenible. "
                    f"Para cubrir materiales, gastos y tu tiempo, debería estar al menos en **{money(math.ceil(min_s))}**."
                )
            elif r["price"] < ideal_s:
                st.warning(
                    "🟡 Este servicio cubre el mínimo, pero deja poco margen. "
                    "No está necesariamente mal, pero puede estar frenando tu ganancia."
                )
            else:
                st.success(
                    "🟢 Este servicio está bien posicionado o por encima del mínimo recomendado."
                )

            st.divider()

        st.subheader("📊 Resultado global del negocio")

        st.write(diagnosis(profit_hour, desired_hour))

        st.write(f"💰 **Ingresos totales del mes:** {money(total_income)}")
        st.write(f"🧴 **Materiales usados:** {money(total_material)}")
        st.write(f"🏠 **Gastos del negocio:** {money(business_expenses)}")
        st.write(f"💸 **Gastos totales:** {money(total_expenses)}")
        st.write(f"✅ **Ganancia real aproximada:** {money(profit)}")
        st.write(f"⏱️ **Horas trabajadas al mes:** {total_hours:.1f} horas")
        st.write(f"💵 **Ganancia real por hora:** {profit_hour:.2f} €/h")

        st.divider()

        st.subheader("🧠 Interpretación global")

        if profit < 0:
            st.error(
                "🔴 Tu negocio está en pérdida. "
                "Estás gastando más de lo que ingresas. Antes de crecer, necesitas revisar precios, gastos o servicios."
            )

        elif profit_hour < desired_hour:
            st.warning(
                "🟡 Tu negocio deja ganancia, pero no estás alcanzando la referencia por hora que elegiste. "
                "Esto significa que no necesariamente estás perdiendo dinero, pero sí podrías estar cobrando poco para el tiempo que inviertes."
            )

        else:
            st.success(
                "🟢 Tu negocio es rentable y estás alcanzando tu referencia por hora. "
                "Tus precios tienen una estructura más sana."
            )

        st.divider()

        st.subheader("🚨 Servicio que más puede estar afectando tu rentabilidad")

        worst_service = min(analyzed_services, key=lambda x: x["total_impact"])

        st.write(f"El servicio que más puede estar bajando tu rentabilidad es: **{worst_service['name']}**")

        st.write(f"Precio actual: **{money(worst_service['price'])}**")
        st.write(f"Precio mínimo recomendado: **{money(worst_service['min_price'])}**")
        st.write(f"Diferencia frente al mínimo: **{money(worst_service['gap_to_minimum'])}**")
        st.write(f"Impacto mensual aproximado: **{money(worst_service['total_impact'])}**")

        if worst_service["gap_to_minimum"] < 0:
            st.error(
                f"Este servicio está por debajo del mínimo. "
                f"Deberías revisar este primero antes de subir todos tus precios."
            )
        elif worst_service["real_profit_per_hour"] < desired_hour:
            st.warning(
                "Este servicio no está necesariamente en pérdida, pero paga peor tu tiempo que otros servicios."
            )
        else:
            st.success(
                "No hay un servicio claramente ruinoso, pero este es el que deja menos margen comparado con los demás."
            )

        st.divider()

        st.subheader("✅ Recomendación práctica")

        red_services = [s for s in analyzed_services if s["price"] < s["min_price"]]
        yellow_services = [s for s in analyzed_services if s["price"] >= s["min_price"] and s["price"] < s["ideal_price"]]

        if red_services:
            st.write("Servicios que deberías revisar primero:")

            for s in red_services:
                st.write(
                    f"🔴 **{s['name']}** — precio actual: {money(s['price'])}, "
                    f"mínimo recomendado: {money(math.ceil(s['min_price']))}"
                )

            st.info(
                "No tienes que subir todo de golpe. Empieza por los servicios rojos, "
                "porque son los que más sentido tiene corregir primero."
            )

        elif yellow_services:
            st.write("Servicios que cubren el mínimo, pero podrían mejorar margen:")

            for s in yellow_services:
                st.write(
                    f"🟡 **{s['name']}** — precio actual: {money(s['price'])}, "
                    f"ideal recomendado: {money(math.ceil(s['ideal_price']))}"
                )

            st.info(
                "Estos servicios no están mal, pero si quieres ganar mejor por hora, "
                "puedes ajustar algunos poco a poco."
            )

        else:
            st.success(
                "Tus servicios están bien estructurados según los datos que introdujiste. "
                "Puedes enfocarte en mejorar presentación, fotos, packs, diseños premium o conseguir más clientas."
            )

        st.divider()

        if rent > 0:
            st.info(
                "El alquiler/silla/local se reparte entre todos tus servicios. "
                "Si haces pocos servicios al mes, cada servicio carga más gasto."
            )

        if commission > 0:
            st.info(
                "La comisión del salón reduce lo que realmente te queda de cada servicio."
            )

        if travel_month > 0 or travel_time > 0:
            st.info(
                "A domicilio debe salir diferente a casa porque sumas desplazamiento mensual y/o tiempo extra."
            )

        if tools_month > 0:
            st.info(
                f"Estás repartiendo tu inversión en herramientas como {money(tools_month)} al mes."
            )

        st.caption(
            "Este cálculo no pretende decirte el precio exacto del mercado. "
            "Sirve para saber si tus precios cubren materiales, gastos y el valor de tu tiempo."
        )

        st.info(
            "Este cálculo no representa el precio de mercado de tu zona. "
            "Representa el precio que necesitarías cobrar para cubrir materiales, gastos y el valor de tu tiempo. "
            "Si los precios recomendados parecen altos, no significa que estén mal: significa que el mercado y tu rentabilidad no siempre coinciden."
        )

        st.caption(
            "Los precios del mercado cambian según ciudad, país y tipo de clienta. "
            "Por eso esta herramienta no adivina precios locales: calcula si tus propios números son sostenibles."
        )
