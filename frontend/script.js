document.addEventListener('DOMContentLoaded', () => {
    
    // --- START SCREEN LOGIC ---
    const startBtn = document.getElementById('start-btn');
    const startScreen = document.getElementById('start-screen');
    const gameView = document.getElementById('game-view');

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            // 1. Add fade-out animation to start screen
            startScreen.classList.add('fade-out');
            
            // 2. Wait for animation (500ms) then switch views
            setTimeout(() => {
                startScreen.style.display = 'none';
                gameView.style.display = 'flex'; // Show game
            }, 500);
        });
    }

    // --- GAME LOGIC ---
    const ROWS = 6;
    const COLS = 7;
    let board = [];
    let gameActive = true; 
    let humanScore = 0;
    let aiScore = 0;

    function initGame() {
        const boardEl = document.getElementById('board');
        boardEl.innerHTML = '';
        board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
        
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.id = `cell-${r}-${c}`;
                cell.onclick = () => handleMove(c);
                boardEl.appendChild(cell);
            }
        }
        gameActive = true;
        document.getElementById('status').innerText = "Your Turn (Red)";
    }

    function placePieceUI(row, col, player) {
        const cell = document.getElementById(`cell-${row}-${col}`);
        if (player === 1) cell.classList.add('red');
        if (player === 2) cell.classList.add('yellow');
    }

    function checkWin(player) {
        // Horizontal
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS - 3; c++) {
                if (board[r][c] === player && board[r][c+1] === player && 
                    board[r][c+2] === player && board[r][c+3] === player) {
                    return [[r,c], [r,c+1], [r,c+2], [r,c+3]]; 
                }
            }
        }
        // Vertical
        for (let c = 0; c < COLS; c++) {
            for (let r = 0; r < ROWS - 3; r++) {
                if (board[r][c] === player && board[r+1][c] === player && 
                    board[r+2][c] === player && board[r+3][c] === player) {
                    return [[r,c], [r+1,c], [r+2,c], [r+3,c]];
                }
            }
        }
        // Diagonal (/)
        for (let r = 0; r < ROWS - 3; r++) {
            for (let c = 0; c < COLS - 3; c++) {
                if (board[r][c] === player && board[r+1][c+1] === player && 
                    board[r+2][c+2] === player && board[r+3][c+3] === player) {
                    return [[r,c], [r+1,c+1], [r+2,c+2], [r+3,c+3]];
                }
            }
        }
        // Diagonal (\)
        for (let r = 3; r < ROWS; r++) {
            for (let c = 0; c < COLS - 3; c++) {
                if (board[r][c] === player && board[r-1][c+1] === player && 
                    board[r-2][c+2] === player && board[r-3][c+3] === player) {
                    return [[r,c], [r-1,c+1], [r-2,c+2], [r-3,c+3]];
                }
            }
        }
        return null;
    }

    function checkDraw() {
        for (let c = 0; c < COLS; c++) {
            if (board[0][c] === 0) return false; 
        }
        return true; 
    }

    function endGame(winner, winningCells = null) {
        gameActive = false;
        const status = document.getElementById('status');
        
        if (winningCells) {
            winningCells.forEach(([r, c]) => {
                const cell = document.getElementById(`cell-${r}-${c}`);
                if (cell) cell.classList.add('winner');
            });
        }

        if (winner === 'Human') {
            status.innerHTML = "🎉 YOU WIN! 🎉";
            humanScore++;
            document.getElementById('score-human').innerText = humanScore;
        } else if (winner === 'AI') {
            status.innerHTML = "🤖 AI WINS! 🤖";
            aiScore++;
            document.getElementById('score-ai').innerText = aiScore;
        } else {
            status.innerHTML = "🤝 IT'S A DRAW! 🤝";
        }
    }

    async function handleMove(col) {
        if (!gameActive) return;

        let row = -1;
        for (let r = ROWS - 1; r >= 0; r--) {
            if (board[r][col] === 0) {
                row = r;
                break;
            }
        }
        if (row === -1) return;

        board[row][col] = 1; 
        placePieceUI(row, col, 1);

        const humanWinCoords = checkWin(1);
        if (humanWinCoords) {
            endGame('Human', humanWinCoords);
            return;
        }
        
        if (checkDraw()) {
            endGame('Draw');
            return;
        }

        document.getElementById('status').innerHTML = '<div class="spinner"></div> AI is thinking...';

        const depthLevel = parseInt(document.getElementById('difficulty').value);

        try {
            const response = await fetch('http://127.0.0.1:8000/get-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ board: board, depth: depthLevel }) 
            });
            const data = await response.json();
            
            if (data.column === -1) {
                endGame('Draw');
                return;
            }

            const aiCol = data.column;
            let aiRow = -1;
            for (let r = ROWS - 1; r >= 0; r--) {
                if (board[r][aiCol] === 0) {
                    aiRow = r;
                    break;
                }
            }

            if (aiRow !== -1) {
                board[aiRow][aiCol] = 2; 
                placePieceUI(aiRow, aiCol, 2);

                const aiWinCoords = checkWin(2);
                if (aiWinCoords) {
                    endGame('AI', aiWinCoords);
                } else if (checkDraw()) {
                    endGame('Draw');
                } else {
                    document.getElementById('status').innerText = "Your Turn (Red)";
                }
            }
            
        } catch (error) {
            console.error("Error talking to AI:", error);
        }
    }

    // --- MODAL & THEME LOGIC ---
    const modal = document.getElementById("rules-modal");
    const rulesBtn = document.getElementById("rules-btn");
    const closeSpan = document.getElementsByClassName("close-btn")[0];
    const themeBtn = document.getElementById('theme-btn');
    const body = document.body;

    if (rulesBtn) rulesBtn.onclick = function() { modal.style.display = "flex"; }
    if (closeSpan) closeSpan.onclick = function() { modal.style.display = "none"; }
    window.onclick = function(event) {
        if (event.target == modal) modal.style.display = "none";
    }

    if (themeBtn) {
        themeBtn.onclick = () => {
            body.classList.toggle('light-mode');
            if (body.classList.contains('light-mode')) {
                themeBtn.innerText = "🌙"; 
            } else {
                themeBtn.innerText = "☀️"; 
            }
        };
    }

    window.resetGame = initGame;
    initGame();
});