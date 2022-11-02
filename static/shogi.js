// ============ CONSTANTS ========================
// isLoading = false;
// line color
var LINE_COLOR = '#000000';
// line stroke style
var LINE_STROKE_STYLE = { stroke: LINE_COLOR, strokeWidth: 1, selectable: false, evented: false };

// canvas size
var CANVAS_PADDING = 45;
var CANVAS_WIDTH = 465;
var CANVAS_HEIGHT = 615;

// board columns
var BOARD_COL = 5;
// board rows
var BOARD_ROW = 7;
// board cell size
var BOARD_CELL_WIDTH = (CANVAS_WIDTH - CANVAS_PADDING * 2) / (BOARD_COL - 1);
var BOARD_CELL_HEIGHT = (CANVAS_HEIGHT - CANVAS_PADDING * 2) / (BOARD_ROW - 1);
// chess icon size
var CHESS_ICON_SIZE = 60;

// ============ GAME STATE ============
var canvas;
var legal_actions = [];
var isChessSelected = false;
var turns = 0;
var abortController = new AbortController();
var isOnHover = false;

// ============ DRAW BACKGROUND BOARD ============
function drawBackground(canvas) {
    // draw horizontal line
    for (var i = 0; i < BOARD_ROW; i++) {
        canvas.add(
            new fabric.Line(
                [
                    CANVAS_PADDING,
                    BOARD_CELL_HEIGHT * i + CANVAS_PADDING,
                    CANVAS_WIDTH - CANVAS_PADDING,
                    BOARD_CELL_HEIGHT * i + CANVAS_PADDING,
                ],
                LINE_STROKE_STYLE
            )
        );
    }
    // draw vertical line
    for (var i = 0; i < BOARD_COL; i++) {
        canvas.add(
            new fabric.Line(
                [
                    BOARD_CELL_WIDTH * i + CANVAS_PADDING,
                    CANVAS_PADDING,
                    BOARD_CELL_WIDTH * i + CANVAS_PADDING,
                    CANVAS_HEIGHT - CANVAS_PADDING,
                ],
                LINE_STROKE_STYLE
            )
        );
    }
    // 城内の斜め線
    canvas.add(
        new fabric.Line(
            [
                BOARD_CELL_WIDTH + CANVAS_PADDING,
                CANVAS_PADDING,
                BOARD_CELL_WIDTH * 3 + CANVAS_PADDING,
                BOARD_CELL_HEIGHT * 2 + CANVAS_PADDING,
            ],
            LINE_STROKE_STYLE
        )
    );
    canvas.add(
        new fabric.Line(
            [
                BOARD_CELL_WIDTH * 3 + CANVAS_PADDING,
                CANVAS_PADDING,
                BOARD_CELL_WIDTH + CANVAS_PADDING,
                BOARD_CELL_HEIGHT * 2 + CANVAS_PADDING,
            ],
            LINE_STROKE_STYLE
        )
    );
    canvas.add(
        new fabric.Line(
            [
                BOARD_CELL_WIDTH + CANVAS_PADDING,
                CANVAS_PADDING + BOARD_CELL_HEIGHT * 4,
                BOARD_CELL_WIDTH * 3 + CANVAS_PADDING,
                BOARD_CELL_HEIGHT * 6 + CANVAS_PADDING,
            ],
            LINE_STROKE_STYLE
        )
    );
    canvas.add(
        new fabric.Line(
            [
                BOARD_CELL_WIDTH * 3 + CANVAS_PADDING,
                CANVAS_PADDING + BOARD_CELL_HEIGHT * 4,
                BOARD_CELL_WIDTH + CANVAS_PADDING,
                BOARD_CELL_HEIGHT * 6 + CANVAS_PADDING,
            ],
            LINE_STROKE_STYLE
        )
    );
}

// ============ DRAW CHESS =================
function drawChess(canvas, komas, tagloc) {
    const oldBots = canvas.getObjects().filter((e) => ['bot-S', 'bot-E', 'legal-action'].includes(e.objType));

    const files = {
        S: {
            'C1-S': 'RZ.png',
            'C2-S': 'RZ.png',
            'F1-S': 'RF.png',
            'F2-S': 'RF.png',
            'T1-S': 'RT.png',
            'T2-S': 'RT.png',
            'T3-S': 'RT.png',
            'W-S': 'RK.png',
        },
        E: {
            'C1-E': 'GZ.png',
            'C2-E': 'GZ.png',
            'F1-E': 'GF.png',
            'F2-E': 'GF.png',
            'T1-E': 'GT.png',
            'T2-E': 'GT.png',
            'T3-E': 'GT.png',
            'W-E': 'GK.png',
        },
    };

    Object.keys(files.S).map((e) =>
        fabric.Image.fromURL(`/static/images/${files.S[e]}`, function(img) {
            if (tagloc.S[e]) {
                // resize
                img = img.scaleToWidth(CHESS_ICON_SIZE, false);

                // calculate position
                let top = CANVAS_PADDING + (tagloc.S[e][0] - 1) * BOARD_CELL_HEIGHT - CHESS_ICON_SIZE / 2;
                let left = CANVAS_PADDING + (tagloc.S[e][1] - 1) * BOARD_CELL_WIDTH - CHESS_ICON_SIZE / 2;
                img = img.set({ left: left, top: top });

                // disable draggable & control
                img.hasControls = false;
                img.lockMovementX = true;
                img.lockMovementY = true;
                img.objType = 'bot-S';
                img.objId = e;
                img.tag = e;
                canvas.add(img);

                // set cursor
                img.hoverCursor = 'pointer';
            }
        })
    );

    Object.keys(files.E).map((e) =>
        fabric.Image.fromURL(`/static/images/${files.E[e]}`, function(img) {
            if (tagloc.E[e]) {
                // resize
                img = img.scaleToWidth(CHESS_ICON_SIZE, false);

                // calculate position
                let top = CANVAS_PADDING + (tagloc.E[e][0] - 1) * BOARD_CELL_HEIGHT - CHESS_ICON_SIZE / 2;
                let left = CANVAS_PADDING + (tagloc.E[e][1] - 1) * BOARD_CELL_WIDTH - CHESS_ICON_SIZE / 2;
                img = img.set({ left: left, top: top });

                // rotation (only for chess on top)
                img = img.rotate(180);

                // disable draggable & control
                img.hasControls = false;
                img.lockMovementX = true;
                img.lockMovementY = true;
                img.selectable = false;
                img.objType = 'bot-E';
                img.objId = e;
                img.tag = e;
                canvas.add(img);
            }
        })
    );

    canvas.remove(...oldBots);
}

// ============ DRAW LEGAL ACTIONS =================
function drawLegalActions(canvas, points, tag) {
    canvas.remove(...legal_actions);
    legal_actions = [];

    if (isOnHover) {
        points.map((point) => {
            var circle = new fabric.Circle({
                top: CANVAS_PADDING + (point[0] - 1) * BOARD_CELL_HEIGHT - 12,
                left: CANVAS_PADDING + (point[1] - 1) * BOARD_CELL_WIDTH - 12,
                radius: 12,
                fill: 'red',
            });

            circle.hasControls = false;
            circle.lockMovementX = true;
            circle.lockMovementY = true;
            circle.hoverCursor = 'pointer';
            circle.objType = 'legal_action';
            circle.tag = tag;
            circle.nx = point[1];
            circle.ny = point[0];
            canvas.add(circle);
            legal_actions.push(circle);
        });
    }
}

// ===================== HELPER FUNCTION =====================

async function _fetch(url) {
    abortController.abort();
    abortController = new AbortController();
    return await fetch(url, { signal: abortController.signal });
}

async function handleStartGame(level) {
    document.getElementById('message').innerText = '';
    document.getElementById('kihu').value = '';

    var response = await _fetch(`/init_data?search_level=${level}`);
    var data = await response.json();

    drawChess(canvas, data.komas, data.tagloc);

    canvas.on('mouse:over', async function(e) {
        // if (isLoading) return;
        // isLoading = true;
        try {
            if (e.target && e.target.objType == 'bot-S' && !isChessSelected) {
                isOnHover = true;
                var response = await _fetch(`/legal_actions?tag=${e.target.tag}`);
                // isLoading = false;
                var data = await response.json();
                drawLegalActions(canvas, data, e.target.tag);
            }
        } finally {
            // isLoading = false;
        }
    });

    canvas.on('mouse:out', function(e) {
        if (e.target && !isChessSelected) {
            canvas.remove(...legal_actions);
            legal_actions = [];
            isOnHover = false;
        }
    });

    canvas.on('mouse:down', async function(e) {
        // if(isLoading) return;
        if (e.target && e.target.objType == 'bot-S') {
            isChessSelected = !isChessSelected;
        } else if (e.target && e.target.objType == 'legal_action') {
            // isLoading = true;
            const response = await _fetch(encodeURI(`/press_legal_actions?tag=${e.target.tag}&nx=${e.target.nx}&ny=${e.target.ny}`));
            // isLoading = false;
            const data = await response.json();

            canvas.remove(...legal_actions);

            drawChess(canvas, data.komas, data.tagloc);
            isChessSelected = false;

            const kihuContainer = document.getElementById('kihu');
            data.kihu.map((e, i) => {
                const t = e.split(' ');
                t[3] = ['A', 'B', 'C', 'D', 'E'][Number(t[3]) - 1];
                kihuContainer.value += `${turns + i} ${t.join(' ')}\n`;
            });
            turns += 2;

            if (data.init_flag == 1) {
                return handeEndGame(data.message);
            }
        }
    });
}

async function handeEndGame(text) {
    canvas.__eventListeners = {};

    document.getElementById('message').innerText = text;
}

// ===================== MAIN LOGIC =====================
(function() {
    var canvasElement = document.getElementById('canvas');
    canvasElement.width = CANVAS_WIDTH;
    canvasElement.height = CANVAS_HEIGHT;

    canvas = new fabric.Canvas('canvas', { backgroundColor: 'aqua' });
    // draw background
    drawBackground(canvas);
})();