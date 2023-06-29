

# new-bingo

遊戲畫面如下
![game](demo\game.png)

執行`main.py`可啟動遊戲

首先會跳出Select Mode視窗，這邊可選擇單機(Offline)或連線(Online)
![image](demo\select-mode-window.png)

單機模式可選擇直接遊玩(play)或是登入/註冊帳號
![image](demo\offline.png)
直接遊玩每次都會從新開始，登入遊玩若中途關閉遊戲，下次會從上次結束的地方開始
  
  
連線模式需先執行`server.py`，啟動後再開始遊戲
![image](demo\online.png)
連線模式中一定要登入遊玩，另外也可在外查看排行榜

連線模式在第一個人開始遊戲後，所有人都要結束同一回合才能抽選下一個數字