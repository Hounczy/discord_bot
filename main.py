import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")



intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

############################################################
NAME_ROLES = {
    "[ELI]" : 1574759603311218738, # legion role id
    "[ACT]" : 1574759727961874462 # act role id
}

LEGION_ID = 1536808225758912702 # server id, feature only available on Legion's discord
WELCOME_CHANNEL_ID = 1536996293497458738 # Legion's welcome channel
############################################################
@bot.event
async def on_ready():
    print(f"We are rdy to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    guild = member.guild
    logger = logging.getLogger("discord")
    staff_channel_id = 1575553046820159639 # to be changed
    staff_role_id = 1536986259438964836 # to be changed

    if guild.id == LEGION_ID:
        welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)

        if isinstance(welcome_channel, discord.TextChannel):
            embed = discord.Embed(
                title = "Welcome to the server!",
                description = "We are glad you are here!",
                color = discord.Color.blue()
            )
            try:
                await welcome_channel.send(
                    content = member.mention,
                    embed = embed,
                    allowed_mentions = discord.AllowedMentions(
                        users = [member], roles = False, everyone = False
                    )
                )
            except discord.HTTPException:
                logger.exception("Could not send the welcome message")
    else:
        logger.warning("Welcome text channel %s was not found", WELCOME_CHANNEL_ID)

    staff_channel = guild.get_channel(staff_channel_id)

    if not isinstance(staff_channel, discord.TextChannel):
        logger.warning("Staff channel %s was not found", staff_channel_id)
        return

    staff_role = guild.get_role(staff_role_id)
    role_prefix = f"{staff_role.mention} " if staff_role is not None else ""
    message = f"{member.mention} joined the server"

    if staff_role is None:
        logger.warning("Staff role %s was not found", staff_role_id)
    else:
        message = f"{staff_role.mention}, {message}"
        allowed_roles = [staff_role]

    try:
        await staff_channel.send(
            content=f"{role_prefix}{member.mention} joined the server.",
            allowed_mentions=discord.AllowedMentions(
                roles=[staff_role] if staff_role is not None else False,
                users=False,
                everyone=False,
            ),
        )
    except discord.HTTPException:
        logging.getLogger("discord").exception("Could not send the staff join alert.")

@bot.event
async def on_member_update(before, after):
    if before.nick == after.nick or after.nick is None:
        return

    nickname = after.nick.strip().casefold()
    matching_role_ids = set()

    for prefix, role_ids in NAME_ROLES.items():
        prefix = prefix.casefold()
        if nickname == prefix or nickname.startswith(f"{prefix} "):
            matching_role_ids.add(role_ids)

    logger = logging.getLogger("discord")

    for role_id in matching_role_ids:
        role = after.guild.get_role(role_id)
        if role is None:
            logger.warning("Nickname role %s was not found", role_id)
            continue

        if role in after.roles:
            continue

        try:
            await after.add_roles(role, reason="Nickname prefix matched")
        except discord.HTTPException:
            logger.exception("COuld not give %s role to member %s", role_id, after.id)

############################################################
bot.run(token, log_level=logging.INFO)