import streamlit as st
import time
from abc import ABC, abstractmethod

# ==========================================
# CONFIGURACIÓN DE STREAMLIT
# ==========================================
st.set_page_config(page_title="RPG: Patrones OOP", page_icon="🎮", layout="wide")

st.title("🛡️ Simulador Interactivo RPG - 5 Patrones de Diseño OOP")
st.markdown("""
Esta es una versión visual y web de tu simulador. Cada sección interactiva te permite utilizar
uno de los patrones de diseño en tiempo real. ¡Crea personajes, equípalos y lanza eventos!
""")

st.divider()

# ==========================================
# 1. SINGLETON (Gestión Global del Juego)
# ==========================================
class GameManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dia_actual = 1
            cls._instance.historial_global = []
        return cls._instance

# Streamlit reinicia el script en cada interacción.
# Usamos session_state para mantener la instanciación viva (nuestro Singleton práctico en web).
if "gm" not in st.session_state:
    st.session_state.gm = GameManager()

gm_global = st.session_state.gm


# ==========================================
# 2. STRATEGY (Formas de Atacar)
# ==========================================
class AttackStrategy(ABC):
    @abstractmethod
    def execute_attack(self) -> str: pass

class MeleeAttack(AttackStrategy):
    def execute_attack(self) -> str: return "da un potente golpe cuerpo a cuerpo con su arma! ⚔️"

class MagicAttack(AttackStrategy):
    def execute_attack(self) -> str: return "canaliza una brutal descarga mágica a distancia! ☄️"


# ==========================================
# 3. FACTORY METHOD (Fábrica de Personajes)
# ==========================================
class Character(ABC):
    def __init__(self, name: str, strategy: AttackStrategy):
        self.name = name
        self.strategy = strategy
        self.bitacora_personal = []

    @abstractmethod
    def get_description(self) -> str: pass

    @abstractmethod
    def get_power(self) -> int: pass

    def perform_attack(self):
        msg = f"[{self.get_description()}] Nivel {self.get_power()} -> {self.strategy.execute_attack()}"
        self.bitacora_personal.insert(0, msg) # Insertar al inicio para ver lo último primero

class Warrior(Character):
    def __init__(self, name: str):
        super().__init__(name, MeleeAttack())
    def get_description(self) -> str: return f"Guerrero '{self.name}'"
    def get_power(self) -> int: return 100

class Mage(Character):
    def __init__(self, name: str):
        super().__init__(name, MagicAttack())
    def get_description(self) -> str: return f"Mago '{self.name}'"
    def get_power(self) -> int: return 150

class CharacterFactory:
    @staticmethod
    def create_character(char_type: str, name: str) -> Character:
        if char_type == "Guerrero ⚔️": return Warrior(name)
        elif char_type == "Mago 🔮": return Mage(name)
        else: raise ValueError("Clase desconocida.")

# Almacén de personajes jugables en la sesión
if "personajes" not in st.session_state:
    st.session_state.personajes = []


# ==========================================
# 4. DECORATOR (Añadir Estadísticas Dinámicas)
# ==========================================
class CharacterDecorator(Character):
    def __init__(self, character: Character):
        self._wrapped = character

    # Exponemos las propiedades base del personaje original
    @property
    def strategy(self): return self._wrapped.strategy
    @property
    def name(self): return self._wrapped.name
    @property
    def bitacora_personal(self): return self._wrapped.bitacora_personal

    def get_description(self) -> str: return self._wrapped.get_description()
    def get_power(self) -> int: return self._wrapped.get_power()
    def perform_attack(self):
        msg = f"[{self.get_description()}] Nivel Mejorado {self.get_power()} -> {self.strategy.execute_attack()}"
        self.bitacora_personal.insert(0, msg)

class ArmorDecorator(CharacterDecorator):
    def get_description(self) -> str: return self._wrapped.get_description() + " [🛡️ Armadura Pesada]"
    def get_power(self) -> int: return self._wrapped.get_power() + 50

class BlessedDecorator(CharacterDecorator):
    def get_description(self) -> str: return self._wrapped.get_description() + " [✨ Bendición Divina]"
    def get_power(self) -> int: return self._wrapped.get_power() * 2


# ==========================================
# 5. OBSERVER (Eventos Globales del Mundo)
# ==========================================
class Subject(ABC):
    @abstractmethod
    def attach(self, observer): pass
    @abstractmethod
    def notify(self, message: str): pass

class GameEventSystem(Subject):
    def __init__(self):
        self._observers = []
        
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
            
    def notify(self, message: str):
        gm_global.historial_global.insert(0, f"Día {gm_global.dia_actual}: {message}")
        for obs in self._observers:
            obs.update(message)

if "evento_sistema" not in st.session_state:
    st.session_state.evento_sistema = GameEventSystem()
event_sys = st.session_state.evento_sistema

class Observer(ABC):
    @abstractmethod
    def update(self, message: str): pass

class PlayerHUD(Observer):
    def __init__(self, character: Character):
        self.character = character
        
    def update(self, message: str):
        self.character.bitacora_personal.insert(0, f"🔔 SERVIDOR: {message}")


# ==========================================
# --- CONSTRUCCIÓN DE LA INTERFAZ WEB ---
# ==========================================

# SECCIÓN 1: Creación de Personajes (Factory)
st.header("1. Campamento (Factory Method)")
col_fact1, col_fact2 = st.columns([1, 2])

with col_fact1:
    with st.form("crear_pj", clear_on_submit=True):
        st.subheader("Entrenar Nuevo Héroe")
        clase_seleccionada = st.selectbox("Elige la clase:", ["Guerrero ⚔️", "Mago 🔮"])
        nombre_ingresado = st.text_input("Nombre de tu campeón:", "Héroe")
        btn_crear = st.form_submit_button("Crear Personaje 🌟")
        
        if btn_crear:
            nuevo_pj = CharacterFactory.create_character(clase_seleccionada, nombre_ingresado)
            st.session_state.personajes.append(nuevo_pj)
            
            # Al crearlo, lo suscribimos automáticamente al sistema de eventos (Observer)
            nuevo_hud = PlayerHUD(nuevo_pj)
            
            # Guardamos los observers en sesión para que no se pierdan
            if "huds_activos" not in st.session_state:
                st.session_state.huds_activos = []
            st.session_state.huds_activos.append(nuevo_hud)
            event_sys.attach(nuevo_hud)
            
            st.rerun()

with col_fact2:
    st.info("💡 **Factory Method:** Se oculta la complejidad. Tú solo pides un string ('Mago' o 'Guerrero') y la fábrica instancia el objeto concreto correcto sin que te preocupes por el 'new Mage()'")

st.divider()

# SECCIÓN 2: Listado y Mejoras (Decorator & Strategy)
st.header("2. Grupo de Héroes Activos (Decorator & Strategy)")
if not st.session_state.personajes:
    st.warning("No tienes personajes creados. ¡Crea uno en el campamento!")
else:
    for idx, personaje in enumerate(st.session_state.personajes):
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"### {personaje.get_description()}")
                st.markdown(f"**Nivel de Poder:** `{personaje.get_power()}`")
                
                # Bitácora desplegable
                with st.expander("Ver HUD / Bitácora de Acciones"):
                    if not personaje.bitacora_personal:
                        st.write("_Sin acciones recientas._")
                    for log in personaje.bitacora_personal:
                        st.write(f"- {log}")
            
            with c2:
                # Comportamiento Polimórfico (Strategy)
                if st.button("🔥 Atacar", key=f"atk_{idx}", use_container_width=True):
                    personaje.perform_attack()
                    st.rerun()

            with c3:
                # Modificación Dinámica (Decorator)
                if st.button("🛡️ Dar Armadura (+50)", key=f"arm_{idx}", use_container_width=True):
                    # Decoramos el personaje y lo guardamos encima del viejo
                    st.session_state.personajes[idx] = ArmorDecorator(personaje)
                    st.rerun()
                if st.button("✨ Bendecir (Poder x2)", key=f"bnd_{idx}", use_container_width=True):
                    st.session_state.personajes[idx] = BlessedDecorator(personaje)
                    st.rerun()
            st.markdown("---")

# SECCIÓN 3: Eventos Globales (Observer & Singleton)
st.header("3. El Mundo (Observer & Singleton)")
col_ev1, col_ev2 = st.columns([1, 2])

with col_ev1:
    st.markdown(f"#### Día Global Actual: **{gm_global.dia_actual}**")
    st.info("💡 Todos estos eventos son notificados automáticamente a las bitácoras (HUD) de tus personajes vivos usando el **Observer**.")
    
    if st.button("🌅 Avanzar un Día"):
        gm_global.dia_actual += 1
        event_sys.notify("Ha amanecido. Tus personajes han descansado.")
        st.rerun()
        
    if st.button("🐉 Invocación de Dragón"):
        event_sys.notify("¡PELIGRO! Un Dragón anciano obscurece el cielo.")
        st.rerun()

with col_ev2:
    st.markdown("#### Historial del Gestor Global (Singleton)")
    st.info("💡 Solo existe un GameManager. Todo el sistema reporta y lee de este único objeto compartido.")
    if not gm_global.historial_global:
        st.write("_Aún no han ocurrido eventos globales._")
    for event_log in gm_global.historial_global:
        st.write(f"- `{event_log}`")

