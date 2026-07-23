<!-- English -->
<h1 align="center">🩺 System Health — Hermes Desktop Plugin</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Hermes%20Agent-plugin-%236c2bd9">
  <img src="https://img.shields.io/badge/platform-windows%20|%20linux%20|%20macos-blue">
  <img src="https://img.shields.io/badge/python-3.8%2B-green">
  <img src="https://img.shields.io/badge/license-MIT-yellow">
</p>

<p align="center">
  <b>EN</b> · <a href="#-français">FR</a> · <a href="#-español">ES</a> · <a href="#-中文">中文</a>
</p>

A **Hermes Desktop** plugin that adds a "System Health" pane with live system metrics, Hermes token usage, model stats, skills overview, and LLM Wiki observability.

## ✨ Features

| Section | Data |
|---------|------|
| 💻 **System Resources** | CPU, RAM, Disk live gauges |
| 📊 **Token Usage** | Input/output tokens, sessions, messages, tool calls |
| 🤖 **Models Used** | Active models and session counts |
| 🔧 **Skills** | Installed/enabled skill counters |
| 🛠️ **Top Tools** | Most-used Hermes tools |
| 📚 **LLM Wiki** | Wiki page count, entities, concepts |
| 🚪 **Gateway** | Hermes gateway status & update time |

## 📦 Installation

### Prerequisites
- Hermes Agent **desktop app** (v0.19.0+)
- Python 3.8+ with `psutil` (`pip install psutil`)

### 1. Desktop plugin

```bash
mkdir -p ~/.hermes/desktop-plugins/system-health
cp plugin.js ~/.hermes/desktop-plugins/system-health/
```

Then in Hermes Desktop: **⌘K → "Reload desktop plugins"**

### 2. Data collector

```bash
pip install psutil
python collector/collector.py    # Collects and injects data
```

### 3. Automate (optional)

**Linux/macOS (crontab):**
```cron
* * * * * cd /path/to/hermes-system-health && python collector/collector.py
```

**Windows (Task Scheduler):**
```powershell
schtasks /create /tn "HermesSystemHealth" /tr "python C:\path\to\collector\collector.py" /sc minute /mo 1
```

## ⚙️ Configuration

```bash
# Custom wiki
python collector/collector.py --wiki /path/to/wiki

# Custom output
python collector/collector.py --output /path/to/cache

# Custom Hermes path
python collector/collector.py --hermes-python /path/to/python --hermes-cli /path/to/hermes
```

---

<!-- Français -->
<h1 align="center">🩺 System Health — Plugin Hermes Desktop</h1>

<p align="center">
  <a href="#features-english">EN</a> ·
  <b>FR</b> ·
  <a href="#-español">ES</a> ·
  <a href="#-中文">中文</a>
</p>

Un **plugin Hermes Desktop** qui ajoute un panneau "System Health" avec les métriques système en direct, l'utilisation des tokens Hermes, les statistiques des modèles, l'aperçu des compétences et l'observabilité du Wiki LLM.

## ✨ Fonctionnalités

| Section | Données |
|---------|---------|
| 💻 **Ressources Système** | CPU, RAM, Disque (jauges live) |
| 📊 **Tokens (30 jours)** | Tokens entrée/sortie, sessions, messages, appels d'outils |
| 🤖 **Modèles utilisés** | Modèles actifs et nombre de sessions |
| 🔧 **Compétences** | Skills installés / activés |
| 🛠️ **Outils principaux** | Outils Hermes les plus utilisés |
| 📚 **Wiki LLM** | Nombre de pages, entités, concepts |
| 🚪 **Passerelle** | Statut du gateway et heure de mise à jour |

## 📦 Installation

### Prérequis
- Application **Hermes Desktop** (v0.19.0+)
- Python 3.8+ avec `psutil` (`pip install psutil`)

### 1. Plugin desktop

```bash
mkdir -p ~/.hermes/desktop-plugins/system-health
cp plugin.js ~/.hermes/desktop-plugins/system-health/
```

Puis dans Hermes Desktop : **⌘K → "Recharger les plugins"**

### 2. Collecteur de données

```bash
pip install psutil
python collector/collector.py
```

### 3. Automatisation (optionnel)

**Linux/macOS (crontab) :**
```cron
* * * * * cd /chemin/vers/hermes-system-health && python collector/collector.py
```

**Windows (Planificateur) :**
```powershell
schtasks /create /tn "HermesSystemHealth" /tr "python C:\chemin\collector\collector.py" /sc minute /mo 1
```

---

<!-- Español -->
<h1 align="center">🩺 System Health — Plugin de Hermes Desktop</h1>

<p align="center">
  <a href="#features-english">EN</a> ·
  <a href="#-français">FR</a> ·
  <b>ES</b> ·
  <a href="#-中文">中文</a>
</p>

Un **plugin de Hermes Desktop** que añade un panel "System Health" con métricas del sistema en vivo, uso de tokens de Hermes, estadísticas de modelos, resumen de habilidades y observabilidad del Wiki LLM.

## ✨ Características

| Sección | Datos |
|---------|-------|
| 💻 **Recursos del Sistema** | CPU, RAM, Disco (indicadores en vivo) |
| 📊 **Tokens (30 días)** | Tokens de entrada/salida, sesiones, mensajes, llamadas de herramientas |
| 🤖 **Modelos Usados** | Modelos activos y número de sesiones |
| 🔧 **Habilidades** | Skills instalados / activados |
| 🛠️ **Herramientas principales** | Herramientas Hermes más usadas |
| 📚 **Wiki LLM** | Páginas, entidades, conceptos |
| 🚪 **Gateway** | Estado del gateway y hora de actualización |

## 📦 Instalación

### Requisitos previos
- Aplicación **Hermes Desktop** (v0.19.0+)
- Python 3.8+ con `psutil` (`pip install psutil`)

### 1. Plugin de escritorio

```bash
mkdir -p ~/.hermes/desktop-plugins/system-health
cp plugin.js ~/.hermes/desktop-plugins/system-health/
```

Luego en Hermes Desktop: **⌘K → "Recargar plugins"**

### 2. Colector de datos

```bash
pip install psutil
python collector/collector.py
```

### 3. Automatización (opcional)

**Linux/macOS (crontab):**
```cron
* * * * * cd /ruta/a/hermes-system-health && python collector/collector.py
```

**Windows (Programador):**
```powershell
schtasks /create /tn "HermesSystemHealth" /tr "python C:\ruta\collector\collector.py" /sc minute /mo 1
```

---

<!-- 中文 -->
<h1 align="center">🩺 System Health — Hermes 桌面插件</h1>

<p align="center">
  <a href="#features-english">EN</a> ·
  <a href="#-français">FR</a> ·
  <a href="#-español">ES</a> ·
  <b>中文</b>
</p>

一个 **Hermes Desktop 插件**，添加"System Health"面板，显示实时系统指标、Hermes token 使用情况、模型统计、技能概览和 LLM Wiki 可观测性。

## ✨ 功能

| 板块 | 数据 |
|------|------|
| 💻 **系统资源** | CPU、内存、磁盘实时仪表 |
| 📊 **Token 使用 (30天)** | 输入/输出 tokens、会话数、消息数、工具调用 |
| 🤖 **使用的模型** | 活动模型及会话计数 |
| 🔧 **技能** | 已安装/启用的技能统计 |
| 🛠️ **主要工具** | 最常用的 Hermes 工具 |
| 📚 **LLM Wiki** | Wiki 页面数、实体数、概念数 |
| 🚪 **网关** | Hermes 网关状态及更新时间 |

## 📦 安装

### 前提条件
- **Hermes Desktop** 应用程序 (v0.19.0+)
- Python 3.8+ 及 `psutil` (`pip install psutil`)

### 1. 桌面插件

```bash
mkdir -p ~/.hermes/desktop-plugins/system-health
cp plugin.js ~/.hermes/desktop-plugins/system-health/
```

然后在 Hermes Desktop 中：**⌘K → "重新加载插件"**

### 2. 数据收集器

```bash
pip install psutil
python collector/collector.py
```

### 3. 自动化（可选）

**Linux/macOS (定时任务)：**
```cron
* * * * * cd /path/to/hermes-system-health && python collector/collector.py
```

**Windows (任务计划程序)：**
```powershell
schtasks /create /tn "HermesSystemHealth" /tr "python C:\path\to\collector\collector.py" /sc minute /mo 1
```

---

## 📁 Project Structure / Structure du projet / Estructura del proyecto / 项目结构

```
hermes-system-health/
├── plugin.js              ← Hermes Desktop Plugin
├── README.md              ← This file / Ce fichier / Este archivo / 本文件
├── collector/
│   ├── collector.py       ← Cross-platform data collector (psutil / wmic)
│   └── inject.py          ← Data injector into plugin.js
├── docs/
│   └── screenshot.png     ← Screenshot (optional)
└── LICENSE
```

## 🤝 Contributing / Contribuer / Contribuir / 贡献

Pull requests welcome! / Les pull requests sont les bienvenues ! / ¡Las pull requests son bienvenidas ! / 欢迎提交 Pull Request！

## 📜 License / Licence / Licencia / 许可证

MIT — free to use, share, and modify.
