# 第三方与来源

## lib/liuren_core/

- 来源：https://github.com/arlen-liang/liuren-bench （`core/liuren_core`）
- 许可：MIT，Copyright (c) 2026 liuren-bench contributors
- 版本：liuren-core 0.1.0
- 改动：**未修改任何逻辑**，仅移动位置
- 作者自述：通过 720 课自洽检验，九宗门口诀与《六壬大全》逐条对过

## lib/bonefate/

- 用途：袁天罡称骨表的查表实现
- 许可：见原目录说明；本项目只调用其公开表

## 字典与节日数据

- `lib/liuren_core/data/jieqi.json`：节气时刻表，随 liuren_core 一同分发（MIT）

## 古籍

- 《滴天髓》《穷通宝鉴》《子平真诠》《三命通会》《渊海子平》《六壬大全》《毕法赋》
- **这些是公版书。本项目只引书名与篇名，断语文本全部自己写**，不摘原文

## 明确没有用到的

- `ruanxiaoer888/bazi-engine` 的断语库（1001 条）：许可为 CC-BY-NC-SA 4.0，**禁商用**。
  **本项目一条都没抄。** 只参考了它的数据结构（condition / conclusion / source / confidence / suggestion）。
