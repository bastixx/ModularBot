set /P name=Enter folder name:
mkdir %~dp0\production\%name%

copy %~dp0template\ModularBot.py %~dp0\production\%name%\%name%.py
copy %~dp0template\config.txt %~dp0\production\%name%\config.ini

mkdir %~dp0\production\%name%\files
copy NUL %~dp0\production\%name%\files\Endings.txt
copy NUL %~dp0\production\%name%\files\Quotes.txt
copy NUL %~dp0\production\%name%\files\Bets.txt
copy NUL %~dp0\production\%name%\files\PrevWinners.txt
copy NUL %~dp0\production\%name%\files\Titleholder.txt
copy NUL %~dp0\production\%name%\files\PrevBets.txt
copy NUL %~dp0\production\%name%\files\Backseatmessage.txt
copy NUL %~dp0\production\%name%\files\Deaths.txt
copy NUL %~dp0\production\%name%\files\Duestions.txt

mkdir %~dp0\production\%name%\files\raffle
copy NUL %~dp0\production\%name%\files\raffle\Raffles.txt

mkdir %~dp0\production\%name%\files\errorlog
copy NUL %~dp0\production\%name%\files\errorlog\Errorlog.txt

mkdir %~dp0\production\%name%\chatlogs