import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import json
import datetime
import config

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

BUGS_FILE = "data/bugs.json"

def load_bugs():
    if os.path.exists(BUGS_FILE):
        with open(BUGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"bugs": [], "counter": 0}

def save_bugs(data):
    os.makedirs("data", exist_ok=True)
    with open(BUGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class SugerenciaModal(discord.ui.Modal, title="💡 Enviar Sugerencia"):
    titulo = discord.ui.TextInput(
        label="Título de la sugerencia",
        placeholder="Ej: Añadir un nuevo minijuego",
        max_length=100
    )
    descripcion = discord.ui.TextInput(
        label="Descripción de la sugerencia",
        placeholder="Describe tu sugerencia...",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(1518976989015314575)
        if not channel:
            try:
                channel = await bot.fetch_channel(1518976989015314575)
            except Exception:
                await interaction.response.send_message("Error al encontrar el canal de sugerencias.", ephemeral=True)
                return

        embed = discord.Embed(
            title=f"💡 {self.titulo.value}",
            description=self.descripcion.value,
            color=0x2ECC71,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Estado", value="🟡 Pendiente", inline=True)
        embed.add_field(name="Votos", value="0", inline=True)
        embed.set_footer(text=f"Sugerencia de {interaction.user.id} • RickyEdit Games")

        msg = await channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await interaction.response.send_message("Sugerencia enviada correctamente.", ephemeral=True)

class ReseñaModal(discord.ui.Modal, title="📝 Enviar Reseña"):
    titulo = discord.ui.TextInput(
        label="Título",
        placeholder="Ej: La web",
        max_length=100
    )
    comentario = discord.ui.TextInput(
        label="Comentario / Opinión",
        placeholder="Describe tu experiencia...",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )
    puntuacion = discord.ui.TextInput(
        label="Puntuación (1 al 10)",
        placeholder="Ej: 10",
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(1518977023823843509)
        if not channel:
            try:
                channel = await bot.fetch_channel(1518977023823843509)
            except Exception:
                await interaction.response.send_message("Error al encontrar el canal de reseñas.", ephemeral=True)
                return

        try:
            puntuacion_val = int(self.puntuacion.value.strip())
            if not (1 <= puntuacion_val <= 10):
                raise ValueError()
        except ValueError:
            await interaction.response.send_message("La puntuación debe ser un número entero entre 1 y 10.", ephemeral=True)
            return

        rating_bar = " ".join(["<:Mate_Punto:1333496488407339088>"] * puntuacion_val)

        embed = discord.Embed(
            title=f"📝 Reseña: {self.titulo.value}",
            description=self.comentario.value,
            color=0x2ECC71,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Puntuación", value=f"{puntuacion_val}/10\n{rating_bar}", inline=False)
        embed.set_footer(text=f"Feedback de {interaction.user.id} • RickyEdit Games")

        await channel.send(embed=embed)
        await interaction.response.send_message("Reseña enviada correctamente.", ephemeral=True)

class ReportarBugModal(discord.ui.Modal, title="🐛 Reportar Bug"):
    titulo = discord.ui.TextInput(
        label="Título del bug",
        placeholder="Ej: Error al iniciar sesión",
        max_length=100
    )
    descripcion = discord.ui.TextInput(
        label="Descripción del problema",
        placeholder="Describe el bug con detalle...",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )
    pasos = discord.ui.TextInput(
        label="Pasos para reproducir",
        placeholder="1. Ir a...\n2. Hacer click en...\n3. Ocurre el error...",
        style=discord.TextStyle.paragraph,
        max_length=1500,
        required=False
    )
    prioridad = discord.ui.TextInput(
        label="Prioridad (baja / media / alta / crítica)",
        placeholder="media",
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        data = load_bugs()
        data["counter"] += 1
        bug_id = data["counter"]

        prioridad_lower = self.prioridad.value.lower()
        prioridad_config = {
            "baja": {"emoji": "🟢", "color": 0x2ECC71, "text": "BAJA"},
            "media": {"emoji": "🟡", "color": 0xF1C40F, "text": "MEDIA"},
            "alta": {"emoji": "🟠", "color": 0xE67E22, "text": "ALTA"},
            "critica": {"emoji": "🔴", "color": 0xE74C3C, "text": "CRÍTICA"},
            "crítica": {"emoji": "🔴", "color": 0xE74C3C, "text": "CRÍTICA"},
        }
        cfg = prioridad_config.get(prioridad_lower, prioridad_config["media"])

        bug_entry = {
            "id": bug_id,
            "titulo": self.titulo.value,
            "descripcion": self.descripcion.value,
            "pasos": self.pasos.value or "No especificados",
            "prioridad": prioridad_lower,
            "estado": "abierto",
            "autor_id": interaction.user.id,
            "autor_nombre": interaction.user.display_name,
            "fecha": datetime.datetime.now().isoformat()
        }
        data["bugs"].append(bug_entry)
        save_bugs(data)

        embed = discord.Embed(
            title=f"🐛 Bug #{bug_id}: {self.titulo.value}",
            description=self.descripcion.value,
            color=cfg["color"],
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Prioridad", value=f"{cfg['emoji']} {cfg['text']}", inline=True)
        embed.add_field(name="Estado", value="🔴 Abierto", inline=True)
        embed.add_field(name="Reportado por", value=interaction.user.mention, inline=True)

        if self.pasos.value:
            embed.add_field(name="Pasos para reproducir", value=self.pasos.value, inline=False)

        embed.set_footer(text=f"Bug #{bug_id} • RickyEdit Games")

        channel = bot.get_channel(1518976958061482105)
        if not channel:
            try:
                channel = await bot.fetch_channel(1518976958061482105)
            except Exception:
                await interaction.response.send_message("Error al encontrar el canal de bugs.", ephemeral=True)
                return

        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        try:
            thread = await msg.create_thread(name=f"bug-{interaction.user.display_name[:20]}")
            await thread.send("Hilo creado <a:a_Mate_Tick:1333495681066733659>")
        except Exception as e:
            print(f"Error creating thread: {e}")

        bug_entry["message_id"] = msg.id
        save_bugs(data)

        await interaction.response.send_message("Bug reportado correctamente.", ephemeral=True)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(f"Error syncing: {e}")

bot = Bot()

@bot.tree.command(name="sugerencia", description="Enviar una sugerencia")
async def sugerencia_command(interaction: discord.Interaction):
    if interaction.channel_id != 1518977101628178502:
        await interaction.response.send_message(
            "Solo se puede sugerir en https://discord.com/channels/1312435256598466611/1518977101628178502",
            ephemeral=True
        )
        return
    await interaction.response.send_modal(SugerenciaModal())

@bot.tree.command(name="reseña", description="Enviar una reseña")
async def reseña_command(interaction: discord.Interaction):
    if interaction.channel_id != 1518977101628178502:
        await interaction.response.send_message(
            "Solo se puede reseñar en https://discord.com/channels/1312435256598466611/1518977101628178502",
            ephemeral=True
        )
        return
    await interaction.response.send_modal(ReseñaModal())

@bot.tree.command(name="bug", description="Reportar un bug")
async def bug_command(interaction: discord.Interaction):
    if interaction.channel_id != 1518977101628178502:
        await interaction.response.send_message(
            "Solo se puede reportar bugs en https://discord.com/channels/1312435256598466611/1518977101628178502",
            ephemeral=True
        )
        return
    await interaction.response.send_modal(ReportarBugModal())

@bot.tree.command(name="bugs", description="Ver todos los bugs reportados")
@app_commands.describe(estado="Filtrar por estado (abierto / cerrado / todos)")
async def ver_bugs(interaction: discord.Interaction, estado: str = "todos"):
    if interaction.channel_id != 1518977101628178502:
        await interaction.response.send_message(
            "Solo se puede ver bugs en https://discord.com/channels/1312435256598466611/1518977101628178502",
            ephemeral=True
        )
        return
    data = load_bugs()
    bugs = data["bugs"]

    if estado.lower() != "todos":
        bugs = [b for b in bugs if b["estado"] == estado.lower()]

    if not bugs:
        await interaction.response.send_message("✅ No hay bugs reportados con ese filtro.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🐛 Bugs Reportados ({len(bugs)})",
        color=0x5865F2
    )

    prioridad_emoji = {"baja": "🟢", "media": "🟡", "alta": "🟠", "critica": "🔴", "crítica": "🔴"}
    estado_emoji = {"abierto": "🔴", "cerrado": "🟢", "en_progreso": "🟡"}

    for bug in bugs[-25:]:
        prio = prioridad_emoji.get(bug["prioridad"], "⚪")
        est = estado_emoji.get(bug["estado"], "⚪")
        embed.add_field(
            name=f"{prio} #{bug['id']}: {bug['titulo']}",
            value=f"Estado: {est} {bug['estado'].replace('_', ' ').title()}\n"
                  f"Por: {bug['autor_nombre']}\n"
                  f"Prioridad: {prio} {bug['prioridad'].title()}",
            inline=True
        )

    embed.set_footer(text="Use /bug-status para cambiar el estado • RickyEdit Games")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="bug-status", description="Cambiar el estado de un bug")
@app_commands.describe(bug_id="ID del bug", nuevo_estado="Nuevo estado (abierto / en_progreso / cerrado)")
@app_commands.checks.has_permissions(administrator=True)
async def bug_status(interaction: discord.Interaction, bug_id: int, nuevo_estado: str):
    if interaction.channel_id != 1518977101628178502:
        await interaction.response.send_message(
            "Solo se puede resolver bugs en https://discord.com/channels/1312435256598466611/1518977101628178502",
            ephemeral=True
        )
        return
    data = load_bugs()
    bug = next((b for b in data["bugs"] if b["id"] == bug_id), None)

    if not bug:
        await interaction.response.send_message(f"❌ No se encontró el bug #{bug_id}.", ephemeral=True)
        return

    estados_validos = ["abierto", "en_progreso", "cerrado"]
    if nuevo_estado.lower() not in estados_validos:
        await interaction.response.send_message(
            f"❌ Estado no válido. Usa: {', '.join(estados_validos)}",
            ephemeral=True
        )
        return

    bug["estado"] = nuevo_estado.lower()
    save_bugs(data)

    estado_emoji = {"abierto": "🔴", "cerrado": "🟢", "en_progreso": "🟡"}
    embed = discord.Embed(
        title=f"✅ Bug #{bug_id} actualizado",
        description=f"El bug **#{bug_id}: {bug['titulo']}** ahora está:",
        color=0x5865F2
    )
    embed.add_field(
        name="Nuevo estado",
        value=f"{estado_emoji[nuevo_estado.lower()]} {nuevo_estado.replace('_', ' ').title()}"
    )

    await interaction.response.send_message(embed=embed)

async def main():
    async with bot:
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
