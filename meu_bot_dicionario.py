import discord
from discord.ext import commands
import json
import os
import asyncio
import logging

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

# Arquivo para armazenar o dicionário
ARQUIVO_DICIONARIO = 'dicionario.json'

def carregar_dicionario():
    """Carrega o dicionário do arquivo JSON"""
    try:
        with open(ARQUIVO_DICIONARIO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_dicionario(dicionario):
    """Salva o dicionário no arquivo JSON"""
    try:
        with open(ARQUIVO_DICIONARIO, 'w', encoding='utf-8') as f:
            json.dump(dicionario, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar dicionário: {e}")
        return False

# Carregar dicionário inicial
dicionario = carregar_dicionario()

@bot.event
async def on_ready():
    """Evento quando o bot estiver pronto"""
    logger.info(f'✅ Bot {bot.user} conectado com sucesso!')
    logger.info(f'📚 Dicionário carregado com {len(dicionario)} termos')
    
    # Atualizar status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(dicionario)} termos | !ajuda"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Tratamento de erros"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Argumentos faltando!** Use `!ajuda` para ver a sintaxe correta.")
    else:
        logger.error(f"Erro no comando: {error}")

# COMANDOS DO BOT
@bot.command()
async def ajuda(ctx):
    """Mostra todos os comandos disponíveis"""
    embed = discord.Embed(
        title="📚 **COMANDOS DO DICIONÁRIO**",
        description="Aqui estão todos os comandos disponíveis:",
        color=0x00ff00
    )
    
    comandos = [
        ("`!definir <termo> <definição>`", "Adiciona um novo termo ao dicionário"),
        ("`!buscar <termo>`", "Busca a definição de um termo"),
        ("`!listar [página]`", "Lista todos os termos (10 por página)"),
        ("`!remover <termo>`", "Remove um termo do dicionário"),
        ("`!editar <termo> <nova_definição>`", "Edita a definição de um termo"),
        ("`!estatisticas`", "Mostra estatísticas do dicionário"),
        ("`!ajuda`", "Mostra esta mensagem de ajuda")
    ]
    
    for nome, descricao in comandos:
        embed.add_field(name=nome, value=descricao, inline=False)
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command()
async def definir(ctx, termo: str, *, definicao: str):
    """Adiciona um novo termo ao dicionário"""
    termo = termo.lower().strip()
    
    if len(termo) > 50:
        await ctx.send("❌ **Termo muito longo!** Máximo 50 caracteres.")
        return
    
    if len(definicao) > 1000:
        await ctx.send("❌ **Definição muito longa!** Máximo 1000 caracteres.")
        return
    
    if termo in dicionario:
        embed = discord.Embed(
            title="⚠️ **Termo Já Existe**",
            description=f"O termo `{termo}` já existe no dicionário.",
            color=0xffa500
        )
        embed.add_field(
            name="Definição Atual",
            value=dicionario[termo][:200] + "..." if len(dicionario[termo]) > 200 else dicionario[termo],
            inline=False
        )
        embed.add_field(
            name="Ação",
            value="Use `!editar` para modificar a definição.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Adicionar ao dicionário
    dicionario[termo] = definicao
    if salvar_dicionario(dicionario):
        embed = discord.Embed(
            title="✅ **Termo Adicionado**",
            description=f"**{termo}** foi adicionado ao dicionário!",
            color=0x00ff00
        )
        embed.add_field(
            name="Definição",
            value=definicao[:500] + "..." if len(definicao) > 500 else definicao,
            inline=False
        )
        embed.set_footer(text=f"Adicionado por {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ **Erro ao Salvar**",
            description="Ocorreu um erro ao salvar o termo. Tente novamente.",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def buscar(ctx, *, termo: str):
    """Busca a definição de um termo"""
    termo = termo.lower().strip()
    
    if termo in dicionario:
        definicao = dicionario[termo]
        embed = discord.Embed(
            title=f"📖 **{termo.upper()}**",
            description=definicao,
            color=0x0099ff
        )
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ **Termo Não Encontrado**",
            description=f"O termo `{termo}` não foi encontrado no dicionário.",
            color=0xff0000
        )
        embed.add_field(
            name="💡 Dica",
            value="Use `!definir` para adicionar este termo ao dicionário.",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def listar(ctx, pagina: int = 1):
    """Lista todos os termos do dicionário"""
    if not dicionario:
        embed = discord.Embed(
            title="📚 **Dicionário Vazio**",
            description="Nenhum termo foi adicionado ainda.\nUse `!definir` para adicionar o primeiro!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Paginação
    termos = sorted(dicionario.keys())
    itens_por_pagina = 10
    total_paginas = (len(termos) + itens_por_pagina - 1) // itens_por_pagina
    
    if pagina < 1 or pagina > total_paginas:
        pagina = 1
    
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    termos_pagina = termos[inicio:fim]
    
    embed = discord.Embed(
        title="📚 **Todos os Termos**",
        color=0x9370db
    )
    
    lista_termos = "\n".join([f"• **{termo}**" for termo in termos_pagina])
    embed.description = lista_termos
    
    embed.set_footer(text=f"Página {pagina}/{total_paginas} • Total: {len(termos)} termos")
    
    await ctx.send(embed=embed)

@bot.command()
async def remover(ctx, *, termo: str):
    """Remove um termo do dicionário"""
    termo = termo.lower().strip()
    
    if termo not in dicionario:
        embed = discord.Embed(
            title="❌ **Termo Não Encontrado**",
            description=f"O termo `{termo}` não existe no dicionário.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Verificar permissões (opcional: apenas quem adicionou pode remover)
    definicao_removida = dicionario[termo]
    del dicionario[termo]
    
    if salvar_dicionario(dicionario):
        embed = discord.Embed(
            title="🗑️ **Termo Removido**",
            description=f"**{termo}** foi removido do dicionário.",
            color=0x00ff00
        )
        embed.add_field(
            name="Definição Removida",
            value=definicao_removida[:300] + "..." if len(definicao_removida) > 300 else definicao_removida,
            inline=False
        )
        embed.set_footer(text=f"Removido por {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ **Erro ao Remover**",
            description="Ocorreu um erro ao remover o termo. Tente novamente.",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def estatisticas(ctx):
    """Mostra estatísticas do dicionário"""
    total_termos = len(dicionario)
    
    embed = discord.Embed(
        title="📊 **ESTATÍSTICAS DO DICIONÁRIO**",
        color=0x9370db
    )
    
    embed.add_field(name="📚 **Total de Termos**", value=total_termos, inline=True)
    embed.add_field(name="🖥️ **Servidores**", value=len(bot.guilds), inline=True)
    embed.add_field(name="⚡ **Latência**", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    if total_termos > 0:
        # Últimos 3 termos adicionados
        ultimos_termos = list(dicionario.keys())[-3:]
        embed.add_field(
            name="🆕 **Últimos Termos**",
            value=", ".join(ultimos_termos),
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    await ctx.send(embed=embed)

# INICIALIZAÇÃO DO BOT
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ Token do Discord não encontrado!")
        logger.info("💡 Verifique se a variável DISCORD_TOKEN está configurada no Railway")
        exit(1)
    
    logger.info("🚀 Iniciando bot Discord...")
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar bot: {e}")