import os
import discord
import random
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 사용자 자산을 저장할 딕셔너리
user_assets = {}

# 기본 자산 설정 함수
def initialize_user(user_id):
    if user_id not in user_assets:
        user_assets[user_id] = 10000  # 기본 자산 10,000원

# 출석체크 커맨드
@bot.command(name="출석체크")
async def daily_check(ctx):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화
    user_assets[user_id] += 10000  # 출석체크로 10,000원 추가
    await ctx.send(f"{ctx.author.display_name}님, 출석체크로 10,000원을 받았습니다! 현재 자산: {user_assets[user_id]}원")

# 자산 확인 커맨드
@bot.command(name="자산확인")
async def check_asset(ctx):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화
    asset = user_assets.get(user_id, 10000)
    await ctx.send(f"{ctx.author.display_name}님의 현재 자산은 {asset}원입니다.")

# 기본 도박 커맨드
@bot.command(name="도박")
async def gamble(ctx, gamble_amount: int):
    user_id = ctx.author.id
    initialize_user(user_id)
    asset = user_assets[user_id]

    if gamble_amount > asset:
        await ctx.send("도박 금액이 보유 자산보다 많습니다. 다시 입력하세요.")
        return
    elif gamble_amount <= 0:
        await ctx.send("도박 금액은 0보다 커야 합니다. 다시 입력하세요.")
        return

    # 도박 금액 차감
    asset -= gamble_amount
    multiplier = 2  # 기본 배당률
    success = random.choice([True, False])  # 50% 확률

    while True:
        if success:
            win_amount = gamble_amount * multiplier
            await ctx.send(f"🎉 성공! {win_amount}원을 수령하거나 한 번 더 도전할 수 있습니다.")
            await ctx.send("수령하려면 '/수령', 한 번 더 도전하려면 '/도전'을 입력하세요.")

            def check(m):
                return m.author == ctx.author and m.content in ["/수령", "/도전"]

            try:
                response = await bot.wait_for("message", check=check, timeout=30.0)

                if response.content == "/수령":
                    asset += win_amount
                    user_assets[user_id] = asset
                    await ctx.send(f"{win_amount}원을 수령했습니다. 현재 자산: {asset}원")
                    break
                elif response.content == "/도전":
                    multiplier *= 2
                    await ctx.send("배당률을 두 배로 늘리고 한 번 더 도전합니다!")
                    success = random.choice([True, False])  # 다시 성공 여부 결정
            except TimeoutError:
                await ctx.send("시간이 초과되어 도박이 종료되었습니다.")
                break
        else:
            await ctx.send("💸 탕진했습니다... 도박에 실패하여 잔액이 사라집니다.")
            gamble_amount = 0
            break

    user_assets[user_id] = asset  # 최종 자산 저장

# 가위바위보 도박 커맨드

@bot.command(name="가위바위보도박")
async def rps_gamble(ctx, gamble_amount: int):
    user_id = ctx.author.id
    initialize_user(user_id)
    asset = user_assets[user_id]

    if gamble_amount > asset:
        await ctx.send("도박 금액이 보유 자산보다 많습니다. 다시 입력하세요.")
        return
    elif gamble_amount <= 0:
        await ctx.send("도박 금액은 0보다 커야 합니다. 다시 입력하세요.")
        return

    # 가위바위보 시작
    asset -= gamble_amount  # 도박 금액 차감
    rps_options = ["가위", "바위", "보"]
    bot_choice = random.choice(rps_options)

    await ctx.send("가위, 바위, 보 중 하나를 선택하세요! (예: 가위)")

    def check(m):
        return m.author == ctx.author and m.content in rps_options

    try:
        user_response = await bot.wait_for("message", check=check, timeout=30.0)
        user_choice = user_response.content
        await ctx.send(f"당신의 선택: {user_choice} | 봇의 선택: {bot_choice}")

        # 결과 판단
        if (user_choice == "가위" and bot_choice == "보") or \
           (user_choice == "바위" and bot_choice == "가위") or \
           (user_choice == "보" and bot_choice == "바위"):
            # 이긴 경우 두 배 획득
            win_amount = gamble_amount * 2
            asset += win_amount
            await ctx.send(f"🎉 축하합니다! {win_amount}원을 획득하셨습니다. 현재 자산: {asset}원")

        elif user_choice == bot_choice:
            # 비긴 경우 다시 기회 제공
            asset += gamble_amount  # 잃은 금액 복구
            await ctx.send("🤝 비겼습니다! 다시 도전하려면 '/가위바위보도박 [금액]' 명령어를 입력하세요.")

        else:
            # 진 경우 금액 잃음
            await ctx.send(f"💸 아쉽게도 패배했습니다... {gamble_amount}원을 잃었습니다. 현재 자산: {asset}원")

    except TimeoutError:
        await ctx.send("시간이 초과되었습니다. 다시 시도해주세요.")

    user_assets[user_id] = asset  # 최종 자산 저장

@bot.command(name="복권")
async def lottery(ctx):
    user_id = ctx.author.id
    initialize_user(user_id)
    asset = user_assets[user_id]
    ticket_cost = 10000  # 복권 비용

    if asset < ticket_cost:
        await ctx.send("복권을 구입하기 위한 자산이 부족합니다.")
        return

    # 복권 비용 차감
    asset -= ticket_cost

    # 10% 확률로 100,000원 획득
    if random.randint(1, 10) == 1:  # 1에서 10 중 1을 뽑으면 당첨
        win_amount = 100000
        asset += win_amount
        await ctx.send(f"🎉 축하합니다! 복권에 당첨되어 {win_amount}원을 획득하셨습니다. 현재 자산: {asset}원")
    else:
        await ctx.send(f"💸 아쉽게도 복권에 당첨되지 않았습니다. 현재 자산: {asset}원")

    user_assets[user_id] = asset  # 최종 자산 저장

@bot.event
async def on_ready():
    print(f"{bot.user} 이(가) 정상적으로 실행되었습니다!\n")


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}! Hice to meet you!")

bot.run(TOKEN)