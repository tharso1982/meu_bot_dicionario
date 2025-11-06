import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Arquivo para armazenar o dicionário
ARQUIVO_DICIONARIO = 'dicionario.json'

# Carregar dicionário existente
def carregar_dicionario():
    try:
        with open(ARQUIVO_DICIONARIO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Salvar dicionário
def salvar_dicionario(dicionario):
    with open(ARQUIVO_DICIONARIO, 'w', encoding='utf-8') as f:
        json.dump(dicionario, f, ensure_ascii=False, indent=4)

# Dicionário em memória
dicionario = carregar_dicionario()

# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} está online!')
    print(f'📚 Dicionário carregado com {len(dicionario)} termos')
    await bot.change_presence(activity=discord.Game(name="!ajuda para ver comandos"))

# Comando de ajuda
@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(
        title="📚 Comandos do Dicionário",
        description="Comandos disponíveis:",
        color=0x00ff00
    )
    embed.add_field(
        name="!definir <termo> <definição>",
        value="Adiciona um novo termo ao dicionário",
        inline=False
    )
    embed.add_field(
        name="!buscar <termo>",
        value="Busca a definição de um termo",
        inline=False
    )
    embed.add_field(
        name="!listar",
        value="Lista todos os termos disponíveis",
        inline=False
    )
    embed.add_field(
        name="!remover <termo>",
        value="Remove um termo do dicionário",
        inline=False
    )
    embed.add_field(
        name="!estatisticas",
        value="Mostra estatísticas do dicionário",
        inline=False
    )
    await ctx.send(embed=embed)

# Comando para adicionar definição
@bot.command()
async def definir(ctx, termo: str, *, definicao: str):
    termo = termo.lower().strip()
    
    if termo in dicionario:
        embed = discord.Embed(
            title="⚠️ Termo Existente",
            description=f"O termo '{termo}' já existe. Use !editar para modificar.",
            color=0xffa500
        )
        await ctx.send(embed=embed)
        return
    
    dicionario[termo] = definicao
    salvar_dicionario(dicionario)
    
    embed = discord.Embed(
        title="✅ Termo Adicionado",
        description=f"**{termo}**: {definicao}",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

# Comando para buscar definição
@bot.command()
async def buscar(ctx, *, termo: str):
    termo = termo.lower().strip()
    
    if termo in dicionario:
        embed = discord.Embed(
            title=f"📖 {termo.capitalize()}",
            description=dicionario[termo],
            color=0x0099ff
        )
        embed.set_footer(text=f"Termo consultado por {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ Termo Não Encontrado",
            description=f"O termo '{termo}' não existe no dicionário.",
            color=0xff0000
        )
        embed.add_field(
            name="Sugestão",
            value="Use !definir para adicionar este termo",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Comando para listar todos os termos
@bot.command()
async def listar(ctx):
    if not dicionario:
        embed = discord.Embed(
            title="📚 Dicionário Vazio",
            description="Nenhum termo foi adicionado ainda.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    termos = ", ".join(sorted(dicionario.keys()))
    
    # Discord limita a 2000 caracteres por mensagem
    if len(termos) > 1500:
        termos = termos[:1500] + "...\n(use !buscar <termo> para ver definições específicas)"
    
    embed = discord.Embed(
        title="📚 Todos os Termos",
        description=termos,
        color=0x0099ff
    )
    embed.set_footer(text=f"Total de {len(dicionario)} termos")
    await ctx.send(embed=embed)

# Comando para remover termo
@bot.command()
async def remover(ctx, *, termo: str):
    termo = termo.lower().strip()
    
    if termo not in dicionario:
        embed = discord.Embed(
            title="❌ Termo Não Encontrado",
            description=f"O termo '{termo}' não existe no dicionário.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    definicao_removida = dicionario.pop(termo)
    salvar_dicionario(dicionario)
    
    embed = discord.Embed(
        title="🗑️ Termo Removido",
        description=f"**{termo}** foi removido do dicionário.",
        color=0x00ff00
    )
    embed.add_field(
        name="Definição Removida",
        value=definicao_removida[:500],  # Limita o tamanho
        inline=False
    )
    await ctx.send(embed=embed)

# Comando para estatísticas
@bot.command()
async def estatisticas(ctx):
    total_termos = len(dicionario)
    
    embed = discord.Embed(
        title="📊 Estatísticas do Dicionário",
        color=0x9370db
    )
    embed.add_field(name="📚 Total de Termos", value=total_termos, inline=True)
    embed.add_field(name="👥 Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="⚡ Latência", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    if total_termos > 0:
        ultimos_termos = list(dicionario.keys())[-5:]  # Últimos 5 termos
        embed.add_field(
            name="📝 Últimos Termos Adicionados",
            value=", ".join(ultimos_termos),
            inline=False
        )
    
    await ctx.send(embed=embed)

# Comando para editar definição existente
@bot.command()
async def editar(ctx, termo: str, *, nova_definicao: str):
    termo = termo.lower().strip()
    
    if termo not in dicionario:
        embed = discord.Embed(
            title="❌ Termo Não Encontrado",
            description=f"O termo '{termo}' não existe. Use !definir para criá-lo.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    definicao_antiga = dicionario[termo]
    dicionario[termo] = nova_definicao
    salvar_dicionario(dicionario)
    
    embed = discord.Embed(
        title="✏️ Termo Editado",
        description=f"**{termo}** foi atualizado.",
        color=0x00ff00
    )
    embed.add_field(name="Definição Anterior", value=definicao_antiga[:500], inline=False)
    embed.add_field(name="Nova Definição", value=nova_definicao[:500], inline=False)
    await ctx.send(embed=embed)

# Tratamento de erros
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Argumento Faltando",
            description=f"Use: `{ctx.command.name} {ctx.command.signature}`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    else:
        print(f"Erro: {error}")

# Iniciar o bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERRO: Token não encontrado. Verifique o arquivo .env")