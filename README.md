# Trabajo-patrones: Simulador RPG

Esta documentación acompaña al sistema interactivo desarrollado en `app_patrones.py` utilizando Python y Streamlit. A continuación, se expone la justificación teórica y el funcionamiento técnico interno de los patrones de diseño orientados a objetos utilizados.

---

## 1. Reflexión Teórica sobre Patrones de Diseño

Los patrones de diseño en la Programación Orientada a Objetos (POO) no son pedazos de fragmentos de código prefabricados, sino soluciones conceptuales abstractas y probadas para resolver problemas arquitectónicos concurrentes al diseñar software.

Su correcta implementación facilita un software verdaderamente escalable, cohesionado y con bajo acoplamiento. En el contexto de este proyecto (un Videojuego RPG interactivo), aplicar patrones ayuda a ilustrar en un dominio claro cómo múltiples entidades coexisten sin enredarse. 

El uso de estos 5 patrones ilustra directamente los principios **SOLID**, en particular:
*   **Principio Abierto / Cerrado (OCP):** Patrones como *Strategy* y *Decorator* permien añadir nuevas armaduras o formas de atacar sin modificar el código fuente de los personajes (abierto para extensión, cerrado para modificación).
*   **Principio de Responsabilidad Única (SRP):** El *Factory Method* asume únicamente la responsabilidad de instanciar; el *Singleton* asume únicamente la gestión de estado de partidas.
*   **Inversión de Dependencias (DIP):** El *Observer* permite que las clases no dependan unas de otras directamente, sino de interfaces suscriptoras.

---

## 2. Explicación Técnica Detallada por Patrón

### I. Singleton (Patrón Creacional)
*   **Contexto en el código:** Clase `GameManager`
*   **Implementación Técnica:** Su propósito es garantizar que exista una sola y única instancia del núcleo de gestión de estado (días jugados e historial general).
*   **Cómo funciona:** Se sobrescribe el método especial `__new__` de Python. Antes de alojar en memoria el nuevo objeto, comprueba la variable protegida estática `cls._instance`. Si es `None`, procede a llamar a `super().__new__(cls)` alojando por primera vez la memoria del sistema. Si ya existía, omite la creación y retorna el puntero de la instancia ya construida. Al integrarlo en Streamlit, usamos `st.session_state` como ecosistema envolvente para asegurar que las variables sobrevivan al recargado constante de la web.

### II. Strategy (Patrón de Comportamiento)
*   **Contexto en el código:** Interfaz `AttackStrategy` y clases `MeleeAttack`, `MagicAttack`.
*   **Implementación Técnica:** Define familias de algoritmos y los hace intercambiables. 
*   **Cómo funciona:** En lugar de tener la clase base del guerrero evaluando un masivo bloque `if tipo_arma == 'espada': ... elif tipo_arma == 'fuego': ...`, delegamos esta responsabilidad lógica en una interfaz. El Héroe tiene propiedad `self.strategy` inyectada en su constructor. Al solicitar a un héroe que ataque con `perform_attack()`, este simplemente solicita que la estrategia se encargue sin saber qué algoritmo exacto está ocurriendo por debajo (Polimorfismo).

### III. Factory Method (Patrón Creacional)
*   **Contexto en el código:** Clase `CharacterFactory` y jerarquía base `Character` / `Warrior` / `Mage`.
*   **Implementación Técnica:** Delega la construcción y configuración base de un objeto a una clase estática separada.
*   **Cómo funciona:** El método estático `create_character(char_type, name)` aísla toda la lógica condicional para instanciar subclases correctas. Si ingresa "Guerrero", automáticamente llama al constructor de `Warrior()` (el cual, detrás de escena, solicita el "Strategy" de combate cuerpo a cuerpo). El front-end interactúa mediante strings limpios con la fábrica, desacoplando totalmente la interfaz de usuario de las invocaciones directas a constructores concretos.

### IV. Decorator (Patrón Estructural)
*   **Contexto en el código:** Interfaz `CharacterDecorator` y las clases `ArmorDecorator`, `BlessedDecorator`.
*   **Implementación Técnica:** Añade comportamientos o altera valores de un objeto base en pleno tiempo de ejecución, enlazándolo con "envolturas" en lugar de utilizar herencia de subclases jerárquicas gigantes.
*   **Cómo funciona:** Si el usuario pulsa en la aplicación web el botón de "+ Armadura" sobre un personaje previo, el sistema toma el objeto base e inyecta su puntero en un _wrapper_ (`ArmorDecorator(personaje_anterior)`). El decorador hereda desde la clase base `Character`, pero anula `get_power()` de manera tal que, cuando el código pide su actual nivel de poder, el decorador consulta primero con el personaje original (ej. 100) y le suma lógicamente los beneficios del envoltorio (100 + 50 = 150), todo de forma recursiva e invisible para el cliente web real.

### V. Observer (Patrón de Comportamiento)
*   **Contexto en el código:** Interfaz Subjet(`GameEventSystem`) y el Obvervador(`PlayerHUD`).
*   **Implementación Técnica:** Define una dependencia "uno a muchos". Cuando un objeto principal cambia de estado, notifica silenciosamente a los dependientes.
*   **Cómo funciona:** `GameEventSystem` mantiene en la memoria una lista interna de objetos abstractos de tipo `Observer`. Cuando se realiza un evento ambiental en el mundo (ej. "¡Ha aparecido un dragón!"), el Gestor recorre (`for obs in self._observers:`) llamando estandarizadamente a `obs.update(mensaje)`. La inmensa ventaja técnica reside en que el Gestor no sabe ni le interesa de qué clases son aquellos dentro de la lista (desacoplamiento total), resultando que todas las bitácoras o HUDs independientes reaccionen sincrónicamente al mismo llamado.
