#!/bin/bash
# 双模型对比测试模板
# 用法: bash compare_models.sh "<模型A>" "<模型B>" "<提示词>"
# 示例: bash compare_models.sh "darkidol" "goekdenizguelmez/JOSIEFIED-Qwen2.5" "写一段言情..."
# 注意: git-bash 没有 bc，用 awk 计算耗时

MODEL_A="$1"
MODEL_B="$2"
PROMPT="$3"
if [ -z "$MODEL_A" ] || [ -z "$MODEL_B" ] || [ -z "$PROMPT" ]; then
    echo "用法: $0 <模型A> <模型B> <提示词>"
    exit 1
fi

for MODEL in "$MODEL_A" "$MODEL_B"; do
    echo "========== $MODEL =========="
    START=$(date +%s.%N)
    OUTPUT=$(ollama run "$MODEL" "$PROMPT" 2>/dev/null)
    END=$(date +%s.%N)
    ELAPSED=$(awk "BEGIN{print $END - $START}")
    CHARS=$(echo -n "$OUTPUT" | wc -m)
    echo "$OUTPUT"
    echo ""
    echo "--- 耗时: ${ELAPSED}s  字符数: ${CHARS}  约 $(awk "BEGIN{print int($CHARS / $ELAPSED)}") 字符/s ---"
    echo ""
done
