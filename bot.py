import discord
from discord.ext import commands
from discord.ui import View
import asyncio
import os

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1464968098040905911
CANAL_RECRUTAMENTO = 1501617632866996437
CATEGORIA_RECRUTAMENTO = 1501617632866996438
CANAL_LOGS = 1501617632866996439

CARGO_AVALIADOR = 1501617430915715233

CARGOS_RECRUTA = [
    1501617428965228726,
    1501617427493027903,
    1501617434723881012,
    1506121330637144155
]

PATENTE_INICIAL = 1501617427493027903
CARGO_TEMP = 1501617424263413781

BLACKLIST = []
RECRUTANDO = {}
dados = {}

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

perguntas = [
    "📘 Qual seu nome no Roblox?",
    "📘 Qual sua idade? {rp, não fale a sua real.}",
    "📘 Qual a verificação da sua conta?",
    "📘 Já participou de algum exército, Se sim, Quais?",
    "📘 Quais suas qualidades?",
    "📘 Você é leal à GOC?"
]

jj = [
    "UM!",
    "DOIS!",
    "TRÊS!",
    "QUATRO!",
    "CINCO!",
    "SEIS!",
    "SETE!",
    "OITO!",
    "NOVE!",
    "DEZ!"
]

quiz = [

    {
        "pergunta": 'O instrutor pergunta "Entenderam?", Oque voçês Respondem?"',
        "opcoes": [
            "Sim.",
            "Tô ligado",
            "Sim, senhor.",
            "Aham"
        ],
        "correta": "Sim, senhor."
    },

    {
        "pergunta": "Um superior passa na sua frente, Oque voçê ira falar?",
        "opcoes": [
            "Saudações.",
            "Olá",
            "Ignorar",
            "E ai"
        ],
        "correta": "Saudações."
    },

    {
        "pergunta": "O que significa PPS?",
        "opcoes": [
            "Permissão Para Sair",
            "Bater no meu amigo",
            "Permissão para auxiliar",
            "Permissão Para Atirar"
        ],
        "correta": "Permissão Para Sair"
    }

]

def embed_padrao(titulo, descricao):

    return discord.Embed(
        title=titulo,
        description=descricao,
        color=discord.Color.blue()
    )

class Painel(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="INICIAR RECRUTAMENTO",
        style=discord.ButtonStyle.primary,
        emoji="📘"
    )

    async def iniciar(self, interaction: discord.Interaction, button):

        guild = interaction.guild
        user = interaction.user

        if user.id in BLACKLIST:

            return await interaction.response.send_message(
                "❌ Você está blacklistado.",
                ephemeral=True
            )

        if user.id in RECRUTANDO:

            return await interaction.response.send_message(
                "❌ Você já possui recrutamento aberto.",
                ephemeral=True
            )

        RECRUTANDO[user.id] = True

        categoria = guild.get_channel(
            CATEGORIA_RECRUTAMENTO
        )

        overwrites = {

            guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

            user:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),

            guild.me:
            discord.PermissionOverwrite(
                view_channel=True
            )
        }

        canal = await guild.create_text_channel(
            name=f"📘・recrutamento-{user.name}",
            overwrites=overwrites,
            category=categoria
        )

        await interaction.response.send_message(
            f"✅ Recrutamento criado: {canal.mention}",
            ephemeral=True
        )

        logs = bot.get_channel(CANAL_LOGS)

        if logs:

            await logs.send(
                f"📘 Novo recrutamento iniciado por {user.mention}"
            )

        cargo_temp = guild.get_role(CARGO_TEMP)

        if cargo_temp:

            await user.add_roles(cargo_temp)

        dados[user.id] = {
            "respostas": [],
            "quiz": [],
            "acertos": 0
        }

        class Cancelar(View):

            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(
                label="CANCELAR",
                style=discord.ButtonStyle.red
            )

            async def cancelar(self, interaction2, button):

                if interaction2.user != user:
                    return

                RECRUTANDO.pop(user.id, None)

                await interaction2.response.send_message(
                    "❌ Recrutamento cancelado.",
                    ephemeral=True
                )

                await canal.delete()

        await canal.send(
            user.mention,
            embed=embed_padrao(
                "👋 Bem-vindo",
                "📘 Responda corretamente todas as perguntas."
            ),
            view=Cancelar()
        )

        def check(m):

            return (
                m.author == user and
                m.channel == canal
            )

        for pergunta in perguntas:

            await canal.send(
                embed=embed_padrao(
                    "📘 Pergunta",
                    pergunta
                )
            )

            try:

                resposta = await bot.wait_for(
                    "message",
                    timeout=600,
                    check=check
                )

                dados[user.id]["respostas"].append(
                    (pergunta, resposta.content)
                )

            except asyncio.TimeoutError:

                await canal.send(
                    embed=embed_padrao(
                        "❌ Tempo esgotado",
                        "Recrutamento cancelado."
                    )
                )

                RECRUTANDO.pop(user.id, None)

                await canal.delete()
                return

        class TurnoView(View):

            def __init__(self):
                super().__init__(timeout=300)
                self.turnos = []

            async def add_turno(self, interaction2, turno):

                if turno not in self.turnos:
                    self.turnos.append(turno)

                await interaction2.response.defer()

            @discord.ui.button(
                label="MANHÃ",
                style=discord.ButtonStyle.secondary
            )

            async def manha(self, interaction2, button):
                await self.add_turno(interaction2, "Manhã")

            @discord.ui.button(
                label="TARDE",
                style=discord.ButtonStyle.secondary
            )

            async def tarde(self, interaction2, button):
                await self.add_turno(interaction2, "Tarde")

            @discord.ui.button(
                label="NOITE",
                style=discord.ButtonStyle.secondary
            )

            async def noite(self, interaction2, button):
                await self.add_turno(interaction2, "Noite")

            @discord.ui.button(
                label="ENVIAR",
                style=discord.ButtonStyle.green
            )

            async def enviar(self, interaction2, button):

                dados[user.id]["turnos"] = self.turnos

                await interaction2.response.send_message(
                    "✅ Turnos enviados.",
                    ephemeral=True
                )

                self.stop()

        view_turnos = TurnoView()

        await canal.send(
            embed=embed_padrao(
                "📘 Turnos Disponíveis",
                "Selecione seus turnos."
            ),
            view=view_turnos
        )

        await view_turnos.wait()

        dias_semana = [
            "Segunda",
            "Terça",
            "Quarta",
            "Quinta",
            "Sexta",
            "Sábado",
            "Domingo"
        ]

        class DiasView(View):

            def __init__(self):
                super().__init__(timeout=300)
                self.dias = []

            async def add_dia(self, interaction2, dia):

                if dia not in self.dias:
                    self.dias.append(dia)

                await interaction2.response.defer()

            @discord.ui.button(label="Segunda", style=discord.ButtonStyle.secondary, row=0)
            async def segunda(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[0])

            @discord.ui.button(label="Terça", style=discord.ButtonStyle.secondary, row=0)
            async def terca(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[1])

            @discord.ui.button(label="Quarta", style=discord.ButtonStyle.secondary, row=0)
            async def quarta(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[2])

            @discord.ui.button(label="Quinta", style=discord.ButtonStyle.secondary, row=1)
            async def quinta(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[3])

            @discord.ui.button(label="Sexta", style=discord.ButtonStyle.secondary, row=1)
            async def sexta(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[4])

            @discord.ui.button(label="Sábado", style=discord.ButtonStyle.secondary, row=1)
            async def sabado(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[5])

            @discord.ui.button(label="Domingo", style=discord.ButtonStyle.secondary, row=2)
            async def domingo(self, interaction2, button):
                await self.add_dia(interaction2, dias_semana[6])

            @discord.ui.button(label="ENVIAR", style=discord.ButtonStyle.green, row=2)
            async def enviar(self, interaction2, button):

                dados[user.id]["dias"] = self.dias

                await interaction2.response.send_message(
                    "✅ Dias enviados.",
                    ephemeral=True
                )

                self.stop()

        view_dias = DiasView()

        await canal.send(
            embed=embed_padrao(
                "📘 Dias Disponíveis",
                "Selecione os dias."
            ),
            view=view_dias
        )

        await view_dias.wait()

        class Proximo(View):

            def __init__(self):
                super().__init__(timeout=300)

            @discord.ui.button(
                label="PRÓXIMO",
                style=discord.ButtonStyle.primary
            )

            async def prox(self, interaction2, button):

                await interaction2.response.defer()
                self.stop()

        p1 = Proximo()

        await canal.send(
            embed=embed_padrao(
                "📘 Estratégias de Batalha UNGOC🇺🇳",

                "1. Se tiver algum companheiro de equipe por perto, NÃO aja sozinho.\n"
                "2. Nunca fique no aberto sem proteção.\n"
                "3. Proteja sempre a retaguarda.\n\n"

                "📘 Comandos Militares:\n\n"

                "PPF = Permissão Para Falar\n"
                "PPA = Permissão Para Assistir\n"
                "PPS = Permissão Para Sair\n"
                "PPAX = Permissão Para Auxiliar\n"
                "STS! = Ombro á Ombro\n"
                "CUNHA! = Formação em V\n"
                "FILA ÚNICA! = Uma fila\n"
                "FILA DUPLA! = Duas filas\n"
                "FILA TRIPLA! = Três filas"
            ),
            view=p1
        )

        await p1.wait()

        await canal.send(
            embed=embed_padrao(
                "📘 TESTE JJ",
                "Digite corretamente os comandos, caso voçê não saiba oque é JJ, JJ é nosso polichinelos, por exemplo, um instrutor Ordena fazer 10 JJ."
            )
        )

        indice = 0

        while indice < len(jj):

            palavra = jj[indice]

            await canal.send(
                embed=embed_padrao(
                    "📘 JJ",
                    f"Digite:\n\n{palavra}"
                )
            )

            resposta = await bot.wait_for(
                "message",
                check=check
            )

            if resposta.content.upper() == palavra:

                indice += 1

                await canal.send(
                    embed=embed_padrao(
                        "✅ Correto",
                        "Continue."
                    )
                )

            else:

                indice = 0

                await canal.send(
                    embed=embed_padrao(
                        "❌ Errado",
                        "Recomeçando do UM!"
                    )
                )

        class SaudacaoView(View):

            def __init__(self):
                super().__init__(timeout=300)

            @discord.ui.button(
                label="PRÓXIMO",
                style=discord.ButtonStyle.primary
            )

            async def proximo(self, interaction2, button):

                await interaction2.response.defer()
                self.stop()

        view_s1 = SaudacaoView()

        await canal.send(

            embed=embed_padrao(
                "📘 Comandos Principais",

                "**1. //MAT** — Esse comando é usado para matar alguma coisa.\n\n"

                "**2. //PD PERM** — Esse comando é usado para retirar permanentemente o personagem de alguém.\n\n"

                "**3. //DEF** — Esse comando deve ser usado junto do item escudo.\n\n"

                "**E, por sinal, a nossa saudação geral é: AVANTE G.O.C! 🇺🇳**"
            ),

            view=view_s1
        )

        await view_s1.wait()

        view_s2 = SaudacaoView()

        await canal.send(

            embed=embed_padrao(
                "📘 Saudações 🇺🇳",

                "• Quando encontrar um superior, diga 'Saudações'.\n\n"

                "• Para perguntas de Sim/Não responda:\n"
                "'Sim, Senhor.' ou 'Não, Senhor.'"
            ),

            view=view_s2
        )

        await view_s2.wait()

        await canal.send(
            embed=embed_padrao(
                "✅ JJ Completo",
                "Iniciando quiz final."
            )
        )

        for q in quiz:

            class QuizView(View):

                def __init__(self):
                    super().__init__(timeout=300)

                async def responder(self, interaction2, resposta):

                    dados[user.id]["quiz"].append(
                        (q["pergunta"], resposta)
                    )

                    if resposta == q["correta"]:

                        dados[user.id]["acertos"] += 1

                    await interaction2.response.send_message(
                        "✅ Resposta enviada.",
                        ephemeral=True
                    )

                    self.stop()

                @discord.ui.button(label=q["opcoes"][0], style=discord.ButtonStyle.secondary)
                async def b1(self, interaction2, button):
                    await self.responder(interaction2, q["opcoes"][0])

                @discord.ui.button(label=q["opcoes"][1], style=discord.ButtonStyle.secondary)
                async def b2(self, interaction2, button):
                    await self.responder(interaction2, q["opcoes"][1])

                @discord.ui.button(label=q["opcoes"][2], style=discord.ButtonStyle.secondary)
                async def b3(self, interaction2, button):
                    await self.responder(interaction2, q["opcoes"][2])

                @discord.ui.button(label=q["opcoes"][3], style=discord.ButtonStyle.secondary)
                async def b4(self, interaction2, button):
                    await self.responder(interaction2, q["opcoes"][3])

            view = QuizView()

            await canal.send(
                embed=embed_padrao(
                    "❓ Quiz Final",
                    q["pergunta"]
                ),
                view=view
            )

            await view.wait()

        resultado = dados[user.id]["acertos"]

        relatorio = ""

        for pergunta, resposta in dados[user.id]["respostas"]:

            relatorio += f"{pergunta}\n➡️ {resposta}\n\n"

        relatorio += (
            f"📘 Turnos: {', '.join(dados[user.id].get('turnos', []))}\n"
            f"📘 Dias: {', '.join(dados[user.id].get('dias', []))}\n"
            f"📘 JJ: Completo\n"
            f"📘 Pontuação Quiz: {resultado}/{len(quiz)}\n"
        )

        embed_staff = embed_padrao(
            "📘 NOVO RECRUTAMENTO",
            f"👤 Usuário: {user.mention}\n\n{relatorio}"
        )

        class Staff(View):

            def __init__(self):
                super().__init__(timeout=None)
                self.finalizado = False

            @discord.ui.button(
                label="APROVAR",
                style=discord.ButtonStyle.green,
                emoji="✅"
            )

            async def aprovar(self, interaction2, button):

                if self.finalizado:

                    return await interaction2.response.send_message(
                        "❌ Este recrutamento já foi finalizado.",
                        ephemeral=True
                    )

                self.finalizado = True

                membro = guild.get_member(user.id)

                for cargo_id in CARGOS_RECRUTA:

                    cargo = guild.get_role(cargo_id)

                    if cargo:

                        await membro.add_roles(cargo)

                patente = guild.get_role(PATENTE_INICIAL)

                if patente:

                    await membro.add_roles(patente)

                await interaction2.response.send_message(
                    "✅ Usuário aprovado com sucesso.",
                    ephemeral=True
                )

                await canal.send(
                    embed=embed_padrao(
                        "✅ RECRUTAMENTO APROVADO",
                        f"{user.mention}\n\n"
                        "Parabéns soldado.\n\n"
                        "AVANTE G.O.C 🇺🇳"
                    )
                )

                logs = bot.get_channel(CANAL_LOGS)

                if logs:

                    await logs.send(
                        f"✅ {user.mention} foi aprovado por {interaction2.user.mention}"
                    )

                for item in self.children:
                    item.disabled = True

                await interaction2.message.edit(view=self)

                RECRUTANDO.pop(user.id, None)

                await asyncio.sleep(10)

                await canal.delete()

            @discord.ui.button(
                label="REPROVAR",
                style=discord.ButtonStyle.red,
                emoji="❌"
            )

            async def reprovar(self, interaction2, button):

                if self.finalizado:

                    return await interaction2.response.send_message(
                        "❌ Este recrutamento já foi finalizado.",
                        ephemeral=True
                    )

                self.finalizado = True

                await interaction2.response.send_message(
                    "❌ Usuário reprovado.",
                    ephemeral=True
                )

                await canal.send(
                    embed=embed_padrao(
                        "❌ RECRUTAMENTO REPROVADO",
                        f"{user.mention}\n\n"
                        "Você foi reprovado.\n"
                        "Tente novamente futuramente."
                    )
                )

                logs = bot.get_channel(CANAL_LOGS)

                if logs:

                    await logs.send(
                        f"❌ {user.mention} foi reprovado por {interaction2.user.mention}"
                    )

                for item in self.children:
                    item.disabled = True

                await interaction2.message.edit(view=self)

                RECRUTANDO.pop(user.id, None)

                await asyncio.sleep(10)

                await canal.delete()

        cargo = guild.get_role(
            CARGO_AVALIADOR
        )

        if cargo:

            for membro in cargo.members:

                try:

                    await membro.send(
                        embed=embed_staff,
                        view=Staff()
                    )

                except:
                    pass

        await canal.send(
            embed=embed_padrao(
                "📘 Finalizado",
                "Seu recrutamento foi enviado para avaliação."
            )
        )

@bot.event
async def on_ready():

    print(f"LOGADO COMO {bot.user}")

    canal = bot.get_channel(
        CANAL_RECRUTAMENTO
    )

    embed = embed_padrao(
        "📘 RECRUTAMENTO GOC",
        "Clique abaixo para iniciar."
    )

    await canal.send(
        embed=embed,
        view=Painel()
    )

bot.run(TOKEN)