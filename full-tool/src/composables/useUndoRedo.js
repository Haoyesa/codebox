/**
 * 通用撤销/重做管理器
 * 用法：
 *   const history = useUndoRedo({
 *     maxSteps: 50,
 *     onChange: (state) => { elements.value = state.elements }
 *   });
 *   history.record({ elements: [...elements.value] });
 *   history.undo();
 *   history.redo();
 */
export function useUndoRedo(options = {}) {
  const maxSteps = options.maxSteps || 50;
  const onChange = options.onChange || (() => {});

  const stack = [];
  let index = -1;
  let isUndoing = false;

  function canUndo() { return index > 0; }
  function canRedo() { return index < stack.length - 1; }

  function record(state) {
    // 撤销/重做过程中不记录
    if (isUndoing) return;
    // 丢弃当前指针之后的历史
    if (index < stack.length - 1) {
      stack.splice(index + 1);
    }
    // 深拷贝保存状态
    const snapshot = JSON.parse(JSON.stringify(state));
    stack.push(snapshot);
    // 超过上限时裁剪最旧的历史
    if (stack.length > maxSteps) {
      stack.shift();
    } else {
      index++;
    }
  }

  function undo() {
    if (!canUndo()) return;
    isUndoing = true;
    index--;
    try {
      onChange(JSON.parse(JSON.stringify(stack[index])));
    } finally {
      isUndoing = false;
    }
  }

  function redo() {
    if (!canRedo()) return;
    isUndoing = true;
    index++;
    try {
      onChange(JSON.parse(JSON.stringify(stack[index])));
    } finally {
      isUndoing = false;
    }
  }

  function reset() {
    stack.length = 0;
    index = -1;
  }

  return {
    record,
    undo,
    redo,
    reset,
    canUndo,
    canRedo
  };
}
