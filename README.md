# Fluent TodoList

## 简介

Windows平台待办任务提示软件,采用为微软Fluent Design设计风格  
目前仅仅提供简单待办管理提醒功能

当前UI：  
<img width="1600" height="1200" alt="image" src="https://github.com/user-attachments/assets/432a85cc-c243-4736-ae80-270969d5759b" />

后续新增在 **TodoList 项目** 上新增 **专注计时器（Pomodoro）**

## 后续计划

### 🔹 一、代码架构重新设计

### 📌 目标

- 任务管理（已有功能）和专注计时器（新功能）解耦。
  
- 保证后续可以扩展统计、提醒、跨设备同步。
  
- 避免业务逻辑散落在 UI 层。
  

---

### 1. 模块划分

```bash
TodoList/
├── main.py                 # 程序入口
├── core/                   # 核心业务逻辑
│   ├── tasks.py            # 任务管理（新增、删除、完成状态）
│   ├── focus_timer.py      # 专注计时器逻辑
│   ├── storage.py          # 数据存储（JSON / SQLite）
│   └── stats.py            # 数据统计与分析
├── ui/                     # 界面层
│   ├── main_window.py      # 主窗口（任务列表 + 计时器）
│   ├── timer_widget.py     # 计时器控件（圆形倒计时）
│   ├── task_list_widget.py # 任务列表控件
│   └── stats_window.py     # 统计窗口
└── resources/              # 图标、音效、样式

```

### 2. 核心类设计

#### `Task`（任务类）

```python
class Task:
    def __init__(self, title, deadline=None, priority=0):
        self.title = title
        self.deadline = deadline
        self.priority = priority
        self.completed = False
        self.focus_time_spent = 0  # 专注时间累计（分钟）

```

#### `TaskManager`（任务管理器）

- 增删改查任务
  
- 与存储交互（storage.py）
  

#### `FocusTimer`（专注计时器）

```python
class FocusTimer(QObject):
    tick = pyqtSignal(int)         # 每秒发送剩余时间
    finished = pyqtSignal(str)     # 计时完成（附带任务名）

    def __init__(self, task: Task, duration=25*60):
        super().__init__()
        self.task = task
        self.duration = duration
        self.remaining = duration
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)

```

#### `StatsManager`

- 从存储里读取任务的 `focus_time_spent`
  
- 生成：
  
  - 每日专注时长统计
    
  - 每周趋势
    
  - 任务排名
    

---

### 🔹 二、UI 草图设计

### 主界面布局（`MainWindow`）

```less
+-----------------------------------------------------+
|  菜单栏: 文件 | 统计 | 设置                          |
+-----------------------------------------------------+
|  左侧任务列表 (TaskListWidget)    |  右侧计时器区域   |
|                                   |                  |
|  [ ] 写报告                       |  [任务名：写报告]|
|  [ ] 阅读文档                     |  [  ⏱ 24:59   ] |
|  [ ] 复习英语                     |  [ 开始 / 暂停 ] |
|                                   |  [ 番茄数: 3 ]   |
+-----------------------------------------------------+
|  状态栏: 今日已专注 50 分钟                         |
+-----------------------------------------------------+

```

#### 专注计时器控件（`TimerWidget`）

```less
+-----------------------------+
|   ● 圆形倒计时进度条       |
|                             |
|        24:59                |
|      (任务名：写报告)       |
|                             |
|  [开始] [暂停] [重置]       |
+-----------------------------+

```

#### 统计窗口（`StatsWindow`）

```less
+-------------------------------------------------+
| 专注统计                                        |
+-------------------------------------------------+
| 今日专注： 3 番茄钟 (75 分钟)                   |
| 本周趋势: [折线图]                               |
| 任务专注时间排名：                              |
| 1. 写报告   120分钟                             |
| 2. 阅读文档  45分钟                             |
| 3. 复习英语  30分钟                             |
+-------------------------------------------------+

```

---

### 🔹 三、开发计划（迭代）

#### 阶段 1 – 架构重构

- 抽离 `TaskManager`、`FocusTimer`、`Storage`
  
- 保证任务管理和计时器逻辑独立
  

#### 阶段 2 – 基础计时器

- `TimerWidget` + 简单 UI（开始/暂停/重置）
  
- 倒计时逻辑跑通
  

#### 阶段 3 – 与任务绑定

- 右键任务 → “开始专注”
  
- 专注完成后写入 `focus_time_spent`
  

#### 阶段 4 – 提醒与统计

- 托盘提醒、提示音
  
- `StatsWindow` 显示数据
  

#### 阶段 5 – 界面优化

- 圆形进度条（QPainter）
  
- 深色模式 / 自定义主题
