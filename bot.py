import discord
from discord.ext import commands
import os
import asyncpg
import logging
import traceback

# Configurar logging
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

# Conexão com database
db_pool = None

async def get_db_pool():
    """Obtém ou cria a conexão com o database"""
    global db_pool
    if db_pool is None:
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logger.error("❌ DATABASE_URL não encontrada")
                return None
            
            db_pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("✅ Conexão com database estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com database: {e}")
            return None
    return db_pool

async def init_db():
    """Inicializa o banco de dados"""
    pool = await get_db_pool()
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            # Criar tabela se não existir
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS dicionario (
                    id SERIAL PRIMARY KEY,
                    termo TEXT UNIQUE NOT NULL,
                    definicao TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    data_criacao TIMESTAMP DEFAULT NOW()
                )
            ''')
            logger.info("✅ Tabela dicionario verificada/criada")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar database: {e}")
        return False

# Comandos básicos para teste
@bot.event
async def on_ready():
    logger.info(f'✅ Bot {bot.user} está online!')
    
    # Inicializar database
    success = await init_db()
    if success:
        logger.info("📚 Database pronto para uso")
        await bot.change_presence(activity=discord.Game(name="Database ✅ | !ajuda"))
    else:
        logger.error("❌ Database com problemas")
        await bot.change_presence(activity=discord.Game(name="Database ❌ | !ajuda"))

@bot.command()
async def ping(ctx):
    """Testa a conexão com o bot"""
    latency = round(bot.latency * 1000)
    
    # Testar database também
    pool = await get_db_pool()
    db_status = "✅ Conectado" if pool else "❌ Desconectado"
    
    embed = discord.Embed(title="🏓 **Status do Sistema**", color=0x00ff00)
    embed.add_field(name="⚡ Latência Discord", value=f"{latency}ms", inline=True)
    embed.add_field(name="📊 Database", value=db_status, inline=True)
    embed.add_field(name="🖥️ Host", value="Railway", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def debug_db(ctx):
    """Comando de debug para o database"""
    try:
        pool = await get_db_pool()
        if not pool:
            await ctx.send("❌ **Database não conectado**")
            return
        
        async with pool.acquire() as conn:
            # Contar termos
            count = await conn.fetchval('SELECT COUNT(*) FROM dicionario')
            # Verificar tabela
            table_exists = await conn.fetchval('''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'dicionario'
                )
            ''')
        
        embed = discord.Embed(title="🔧 **Debug Database**", color=0x0099ff)
        embed.add_field(name="📊 Tabela existe", value="✅ Sim" if table_exists else "❌ Não", inline=True)
        embed.add_field(name="📚 Total de termos", value=count, inline=True)
        embed.add_field(name="🌐 Host", value="Railway PostgreSQL", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ **Erro no debug:** {str(e)}")

@bot.command()
async def definir(ctx, termo: str, *, definicao: str):
    """Adiciona um termo ao dicionário"""
    try:
        pool = await get_db_pool()
        if not pool:
            await ctx.send("❌ **Database não disponível.** Tente novamente em alguns segundos.")
            return
        
        termo = termo.lower().strip()
        
        async with pool.acquire() as conn:
            # Verificar se termo já existe
            existing = await conn.fetchrow(
                'SELECT definicao FROM dicionario WHERE termo = $1', 
                termo
            )
            
            if existing:
                # Atualizar
                await conn.execute(
                    'UPDATE dicionario SET definicao = $1, autor = $2 WHERE termo = $3',
                    definicao, str(ctx.author), termo
                )
                action = "atualizado"
            else:
                # Inserir novo
                await conn.execute(
                    'INSERT INTO dicionario (termo, definicao, autor) VALUES ($1, $2, $3)',
                    termo, definicao, str(ctx.author)
                )
                action = "adicionado"
        
        embed = discord.Embed(
            title=f"✅ **Termo {action.capitalize()}**",
            description=f"**{termo}** foi {action} com sucesso!",
            color=0x00ff00
        )
        embed.add_field(name="📝 Definição", value=definicao[:500], inline=False)
        embed.set_footer(text=f"Por {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Erro em !definir: {e}")
        await ctx.send("❌ **Erro ao salvar termo.** Tente novamente.")

@bot.command()
async def buscar(ctx, *, termo: str):
    """Busca um termo no dicionário"""
    try:
        pool = await get_db_pool()
        if not pool:
            await ctx.send("❌ **Database não disponível.** Tente novamente em alguns segundos.")
            return
        
        termo = termo.lower().strip()
        
        async with pool.acquire() as conn:
            resultado = await conn.fetchrow(
                'SELECT termo, definicao, autor, data_criacao FROM dicionario WHERE termo = $1',
                termo
            )
        
        if resultado:
            embed = discord.Embed(
                title=f"📖 **{resultado['termo'].capitalize()}**",
                description=resultado['definicao'],
                color=0x0099ff
            )
            embed.add_field(name="👤 Autor", value=resultado['autor'], inline=True)
            if resultado['data_criacao']:
                data = resultado['data_criacao'].strftime('%d/%m/%Y')
                embed.add_field(name="📅 Data", value=data, inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ **Termo não encontrado:** `{termo}`")
            
    except Exception as e:
        logger.error(f"Erro em !buscar: {e}")
        await ctx.send("❌ **Erro ao buscar termo.** Tente novamente.")

@bot.command()
async def carregar_espinosa(ctx):
    """Carrega os termos da Ética de Espinosa (apenas para administradores)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ **Apenas administradores podem usar este comando.**")
        return
    
    # Dicionário de Espinosa (exemplo reduzido)
    termos_espinosa = {
        "Deus": "Substância absolutamente infinita, constituída por uma infinidade de atributos...",
        "Substância": "Aquilo que existe em si mesmo e é concebido por si mesmo...",
        "Atributo": "Aquilo que o intelecto percebe da substância como constituindo sua essência...",
        "Conatus": "O esforço pelo qual cada coisa se esforça para perseverar em seu ser...",
        "Liberdade": "Existir pela única necessidade de sua natureza e ser determinada a agir por si mesma..."
    }
    
    try:
        pool = await get_db_pool()
        if not pool:
            await ctx.send("❌ **Database não disponível.**")
            return
        
        carregados = 0
        async with pool.acquire() as conn:
            for termo, definicao in termos_espinosa.items():
                try:
                    await conn.execute(
                        'INSERT INTO dicionario (termo, definicao, autor) VALUES ($1, $2, $3) '
                        'ON CONFLICT (termo) DO UPDATE SET definicao = $2',
                        termo.lower(), definicao, "Espinosa - Ética"
                    )
                    carregados += 1
                except Exception as e:
                    logger.error(f"Erro ao inserir {termo}: {e}")
        
        await ctx.send(f"✅ **{carregados} termos de Espinosa carregados com sucesso!**")
        
    except Exception as e:
        logger.error(f"Erro em !carregar_espinosa: {e}")
        await ctx.send("❌ **Erro ao carregar termos.**")

# Inicialização
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        logger.info("🚀 Iniciando bot no Railway...")
        bot.run(token)
    else:
        logger.error("❌ Token não encontrado. Verifique a variável DISCORD_TOKEN.")