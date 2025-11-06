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
    """Carrega TODOS os termos da Ética de Espinosa"""
    
    termos_espinosa = {
        "deus": "Substância absolutamente infinita, constituída por uma infinidade de atributos, cada um dos quais expressa uma essência eterna e infinita.",
        "substância": "Aquilo que existe em si mesmo e é concebido por si mesmo, isto é, aquilo cujo conceito não precisa do conceito de outra coisa do qual deva ser formado.",
        "atributo": "Aquilo que o intelecto percebe da substância como constituindo sua essência.",
        "modo": "As afecções da substância, ou seja, aquilo que existe em outro e é concebido por meio desse outro.",
        "conatus": "O esforço pelo qual cada coisa se esforça para perseverar em seu ser.",
        "liberdade": "Existir pela única necessidade de sua natureza e ser determinada a agir por si mesma.",
        "necessidade": "Todas as coisas são determinadas pela necessidade da natureza divina a existir e a operar de certa maneira.",
        "afecto": "As afecções do corpo, pelas quais sua potência de agir é aumentada ou diminuída, e as ideias dessas afecções.",
        "alegria": "A paixão pela qual a mente passa para uma perfeição maior.",
        "tristeza": "A paixão pela qual a mente passa para uma perfeição menor.",
        "amor": "Alegria acompanhada pela ideia de uma causa exterior.",
        "ódio": "Tristeza acompanhada pela ideia de uma causa exterior.",
        "vontade": "A faculdade de afirmar ou negar, mas não de desejar; em Espinosa, vontade e entendimento são a mesma coisa.",
        "entendimento": "Faculdade de conceber ideias adequadas da essência das coisas.",
        "ideia adequada": "Ideia que, considerada em si mesma, tem todas as propriedades ou denominações intrínsecas de uma ideia verdadeira.",
        "ideia inadequada": "Ideia parcial e confusa que não exprime adequadamente a essência da coisa.",
        "imaginação": "Primeiro gênero de conhecimento, que consiste em ideias inadequadas provenientes dos afetos dos sentidos.",
        "razão": "Segundo gênero de conhecimento, que consiste em noções comuns e ideias adequadas das propriedades das coisas.",
        "ciência intuitiva": "Terceiro gênero de conhecimento, que procede da ideia adequada da essência formal de certos atributos de Deus para a conhecimento adequado da essência das coisas.",
        "natureza naturante": "Deus enquanto considerado como causa livre, ou seja, a substância com seus atributos.",
        "natureza naturada": "Tudo o que segue da necessidade da natureza de Deus, ou seja, todos os modos dos atributos de Deus.",
        "eternidade": "Existência mesma, enquanto concebida como seguindo-se necessariamente da definição de uma coisa eterna.",
        "duratio": "Existência enquanto concebida como começando por alguma causa e continuando por algum tempo.",
        "esperança": "Alegria inconstante nascida da ideia de uma coisa futura ou passada, de cujo desfecho duvidamos.",
        "medo": "Tristeza inconstante nascida da ideia de uma coisa futura ou passada, de cujo desfecho duvidamos.",
        "segurança": "Alegria nascida da ideia de uma coisa futura ou passada, sobre a qual desapareceu toda a dúvida.",
        "desespero": "Tristeza nascida da ideia de uma coisa futura ou passada, sobre a qual desapareceu toda a dúvida.",
        "contentamento": "Alegria acompanhada da ideia de uma causa interior.",
        "melancolia": "Tristeza acompanhada da ideia de uma causa interior.",
        "compaixão": "Amor na medida em que afeta um homem de tal sorte que se alegra com o bem de outrem e se entristece com o mal de outrem.",
        "indignação": "Ódio em relação a alguém que fez mal a outrem.",
        "inveja": "Ódio na medida em que afeta um homem de tal sorte que se entristece com a felicidade alheia e, inversamente, se alegra com o infortúnio alheio.",
        "gratidão": "Desejo ou amor que nos impele a fazer o bem a quem, por um afeto semelhante, nos fez bem.",
        "benevolência": "Desejo de fazer o bem àquele por quem temos compaixão.",
        "ira": "Desejo que nos impele, pelo ódio, a fazer mal àquele que odiamos.",
        "vingança": "Desejo que, pela reciprocidade do ódio, nos impele a fazer mal àquele que, por um afeto semelhante, nos fez mal.",
        "crueldade": "Desejo que impele um homem a fazer mal àquele que amamos ou de quem temos compaixão.",
        "timidez": "Desejo de evitar um mal maior, que tememos, por um mal menor.",
        "audácia": "Desejo que impele alguém a fazer algo com perigo que seus iguais temem enfrentar.",
        "pudor": "Desejo de agradar aos homens, dirigido pela razão.",
        "consternação": "Desejo de evitar o mal, dirigido pela razão.",
        "humanidade": "Desejo de fazer o que agrada aos homens e de evitar o que os desagrada.",
        "ambição": "Desejo imoderado de glória.",
        "luxúria": "Desejo imoderado e amor do intercurso sexual.",
        "gula": "Desejo imoderado de comer.",
        "avareza": "Desejo imoderado de riquezas.",
        "soberba": "Amor de si mesmo que leva o homem a pensar mais altamente de si do que convém.",
        "abjeção": "Tristeza que surge do homem considerar sua própria impotência.",
        "humildade": "Tristeza que surge do homem considerar sua própria impotência ou fraqueza.",
        "devotamento": "Desejo de fazer o bem que nasce do fato de vivermos sob o império da razão.",
        "virtude": "A potência mesma do homem, ou seja, sua essência enquanto tem o poder de fazer coisas que podem ser compreendidas somente pelas leis de sua natureza.",
        "potência": "A essência mesma do homem enquanto tem o poder de produzir certos efeitos que podem ser compreendidos pelas leis de sua natureza.",
        "bondade": "Propriedade pela qual uma coisa se conforma ao nosso conatus e nos é útil.",
        "perfeição": "Realidade ou essência de uma coisa, independentemente de sua duração.",
        "imperfeição": "Privação de perfeição.",
        "bem": "Tudo o que sabemos com certeza ser útil para nós.",
        "mal": "Tudo o que sabemos com certeza nos impedir de participar de algum bem.",
        "beatitude": "O conhecimento intelectual de Deus, que é o amor intelectual de Deus, e que constitui a liberdade humana e a salvação.",
        "salvação": "Estado de liberdade e beatitude que consiste no conhecimento e amor intelectual de Deus.",
        "servidão": "Império dos afetos, isto é, a impotência humana para moderar e refrear os afetos.",
        "homem livre": "Aquele que vive sob a direção da razão e não é guiado pelo medo, mas deseja diretamente o bem.",
        "fortuna": "O poder da natureza externa, que frequentemente se opõe ao nosso conatus.",
        "propriedade comum": "Noção que temos de algo que é comum a todas as coisas e que está igualmente na parte e no todo.",
        "lei natural": "As regras da natureza de cada coisa segundo as quais concebemos que ela é determinada a existir e a operar de certa maneira.",
        "lei divina": "A lei que se refere à verdadeira salvação e beatitude, ou seja, ao conhecimento e amor de Deus.",
        "lei humana": "Regra de vida instituída pelos homens para sua segurança e utilidade.",
        "direito natural": "As próprias leis ou regras da natureza segundo as quais tudo acontece.",
        "estado civil": "A sociedade que se mantém pelo direito civil, isto é, pelo poder da multidão.",
        "pacto social": "Acordo pelo qual os homens transferem seu direito natural à sociedade, que então detém o poder soberano.",
        "democracia": "Assembleia de homens que coletivamente detém o direito soberano.",
        "teologia": "Conhecimento que se refere à lei divina, mas que, segundo Espinosa, deve ser separado da filosofia.",
        "corpo": "Modo da extensão que expressa a essência de Deus enquanto considerada como coisa extensa.",
        "mente": "Ideia do corpo existente em ato, ou seja, o próprio corpo enquanto é concebido sob o atributo do pensamento.",
        "essência": "Aquilo que, sendo dado, põe necessariamente a coisa e, sendo suprimido, suprime necessariamente a coisa.",
        "existência": "A própria atualidade da essência, ou seja, o modo como a coisa se manifesta na realidade.",
        "causa": "Aquilo de que outra coisa qualquer segue necessariamente.",
        "efeito": "Aquilo que segue necessariamente de uma causa.",
        "determinismo": "Doutrina segundo a qual todos os eventos, incluindo o comportamento humano, são determinados por causas anteriores.",
        "panteísmo": "Doutrina que identifica Deus com a natureza ou o universo como um todo.",
        "monismo": "Posição filosófica que afirma que a realidade é constituída por uma única substância.",
        "geometria": "Método utilizado por Espinosa para demonstrar suas proposições filosóficas, seguindo o modelo euclidiano."
    }
    
    carregados = 0
    ja_existiam = 0
    
    for termo, definicao in termos_espinosa.items():
        termo_lower = termo.lower().strip()
        
        if termo_lower not in dicionario:
            dicionario[termo_lower] = {
                'definicao': definicao,
                'autor': "Baruch Espinosa - Ética",
                'data': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            carregados += 1
        else:
            ja_existiam += 1
    
    # Atualizar presença com novo total
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(dicionario)} termos | !ajuda"
        )
    )
    
    embed = discord.Embed(
        title="📚 **ÉTICA DE ESPINOSA - CARREGADA**",
        description=f"**{carregados} novos termos** foram adicionados ao dicionário!",
        color=0x9370db
    )
    
    embed.add_field(
        name="📖 Obra Completa", 
        value="**Ética Demonstrada à Maneira dos Geômetras**\n*Baruch Espinosa (1677)*", 
        inline=False
    )
    
    embed.add_field(name="✅ Novos termos", value=carregados, inline=True)
    embed.add_field(name="📊 Total no dicionário", value=len(dicionario), inline=True)
    
    if ja_existiam > 0:
        embed.add_field(
            name="ℹ️ Termos existentes", 
            value=f"{ja_existiam} termos já estavam no dicionário", 
            inline=False
        )
    
    embed.add_field(
        name="🔍 Exemplos para testar", 
        value="`!buscar deus` `!buscar conatus` `!buscar beatitude`", 
        inline=False
    )
    
    embed.set_footer(text="Use !listar para ver todos os termos disponíveis")
    
    await ctx.send(embed=embed)
    
# INICIALIZAÇÃO
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    
    if token:
        logger.info("🚀 Iniciando bot Discord...")
        bot.run(token)
    else:
        logger.error("❌ Token não encontrado")