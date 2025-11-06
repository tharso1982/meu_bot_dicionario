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