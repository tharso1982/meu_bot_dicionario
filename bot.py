import discord
from discord.ext import commands
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configurações do bot
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

# Dicionário em memória
dicionario = {}

@bot.event
async def on_ready():
    """Quando o bot estiver pronto"""
    logger.info(f'✅ BOT ONLINE: {bot.user.name}')
    logger.info(f'📊 Conectado em {len(bot.guilds)} servidor(es)')
    logger.info(f'📚 Termos no dicionário: {len(dicionario)}')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(dicionario)} termos | !ajuda"
        )
    )

@bot.command()
async def ping(ctx):
    """Testa a conexão do bot"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(title="🏓 **Pong!**", color=0x00ff00)
    embed.add_field(name="⚡ Latência", value=f"{latency}ms", inline=True)
    embed.add_field(name="🖥️ Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="📚 Termos", value=len(dicionario), inline=True)
    embed.add_field(name="💾 Storage", value="Memória 🧠", inline=True)
    embed.add_field(name="🌐 Host", value="Railway 🚂", inline=True)
    embed.add_field(name="🔧 Status", value="Online ✅", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def definir(ctx, termo: str, *, definicao: str):
    """Adiciona um termo ao dicionário"""
    termo = termo.lower().strip()
    
    # Verificar se termo já existe
    if termo in dicionario:
        embed = discord.Embed(
            title="✏️ **Termo Atualizado**",
            description=f"**{termo}** foi atualizado!",
            color=0xffa500
        )
    else:
        embed = discord.Embed(
            title="✅ **Termo Adicionado**",
            description=f"**{termo}** foi adicionado ao dicionário!",
            color=0x00ff00
        )
    
    dicionario[termo] = {
        'definicao': definicao,
        'autor': ctx.author.display_name,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    embed.add_field(name="📝 Definição", value=definicao[:300] + "..." if len(definicao) > 300 else definicao, inline=False)
    embed.set_footer(text=f"Por {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command()
async def buscar(ctx, *, termo: str):
    """Busca a definição de um termo"""
    termo = termo.lower().strip()
    
    if termo in dicionario:
        dados = dicionario[termo]
        
        embed = discord.Embed(
            title=f"📖 **{termo.upper()}**",
            description=dados['definicao'],
            color=0x0099ff
        )
        embed.add_field(name="👤 Autor", value=dados['autor'], inline=True)
        embed.add_field(name="📅 Data", value=dados['data'], inline=True)
    else:
        embed = discord.Embed(
            title="❌ **Termo Não Encontrado**",
            description=f"`{termo}` não existe no dicionário.",
            color=0xff0000
        )
        embed.add_field(
            name="💡 Dica",
            value="Use `!definir` para adicionar este termo",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def listar(ctx):
    """Lista todos os termos"""
    if not dicionario:
        embed = discord.Embed(
            title="📚 **Dicionário Vazio**",
            description="Use `!definir` para adicionar o primeiro termo!\nExemplo: `!definir filosofia estudo da existência`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    termos = list(dicionario.keys())
    
    embed = discord.Embed(
        title="📚 **Todos os Termos**",
        color=0x9370db
    )
    
    # Mostrar até 20 termos
    lista_termos = "\n".join([f"• **{termo}**" for termo in termos[:20]])
    embed.description = lista_termos
    
    if len(termos) > 20:
        embed.set_footer(text=f"Mostrando 20 de {len(termos)} termos • Use !buscar <termo> para ver definições")
    else:
        embed.set_footer(text=f"Total: {len(termos)} termos")
    
    await ctx.send(embed=embed)

@bot.command()
async def ajuda(ctx):
    """Mostra todos os comandos disponíveis"""
    embed = discord.Embed(
        title="📚 **COMANDOS DO DICIONÁRIO**",
        description="Aqui estão todos os comandos disponíveis:",
        color=0x00ff00
    )
    
    comandos = [
        ("`!ping`", "Testa a conexão do bot e mostra estatísticas"),
        ("`!definir <termo> <definição>`", "Adiciona ou atualiza um termo"),
        ("`!buscar <termo>`", "Busca a definição de um termo"),
        ("`!listar`", "Lista todos os termos disponíveis"),
        ("`!carregar_espinosa`", "Carrega termos da Ética de Espinosa"),
        ("`!ajuda`", "Mostra esta mensagem de ajuda")
    ]
    
    for nome, descricao in comandos:
        embed.add_field(name=nome, value=descricao, inline=False)
    
    embed.set_footer(text=f"Bot: {bot.user.name} | Online ✅")
    
    await ctx.send(embed=embed)

@bot.command()
async def carregar_espinosa(ctx):
    """Carrega termos da Ética de Espinosa"""
    termos_espinosa = {
        "deus": "Substância absolutamente infinita, constituída por uma infinidade de atributos, cada um dos quais expressa uma essência eterna e infinita.",
        "substância": "Aquilo que existe em si mesmo e é concebido por si mesmo, isto é, aquilo cujo conceito não precisa do conceito de outra coisa do qual deva ser formado.",
        "atributo": "Aquilo que o intelecto percebe da substância como constituindo sua essência.",
        "modo": "As afecções da substância, ou seja, aquilo que existe em outro e é concebido por meio desse outro.",
        "conatus": "O esforço pelo qual cada coisa se esforça para perseverar em seu ser.",
        "liberdade": "Existir pela única necessidade de sua natureza e ser determinada a agir por si mesma.",
        "necessidade": "Todas as coisas são determinadas pela necessidade da natureza divina a existir e a operar de certa maneira.",
        "afecto": "As afecções do corpo, pelas quais sua potência de agir é aumentada ou diminuída, e as ideias dessas afecções."
    }
    
    carregados = 0
    for termo, definicao in termos_espinosa.items():
        if termo not in dicionario:
            dicionario[termo] = {
                'definicao': definicao,
                'autor': "Espinosa - Ética",
                'data': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            carregados += 1
    
    embed = discord.Embed(
        title="📚 **Espinosa Carregado**",
        description=f"**{carregados}** termos da Ética de Espinosa foram adicionados ao dicionário!",
        color=0x9370db
    )
    embed.add_field(name="📖 Obra", value="Ética, de Baruch Espinosa", inline=False)
    embed.add_field(name="💡 Exemplo", value="Use `!buscar deus` para ver o primeiro conceito", inline=False)
    
    await ctx.send(embed=embed)

# INICIALIZAÇÃO
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    
    if token:
        logger.info("🚀 Iniciando bot Discord...")
        bot.run(token)
    else:
        logger.error("❌ Token não encontrado")