import { inject, ref } from 'vue';

export const ToastSymbol = Symbol('toast');

export function createToast() {
  const message = ref('');
  const type = ref('');
  let timer = null;

  function show(msg, t = '', duration = 2500) {
    message.value = msg;
    type.value = t;
    clearTimeout(timer);
    timer = setTimeout(() => {
      message.value = '';
      type.value = '';
    }, duration);
  }

  return { message, type, show };
}

export function useToast() {
  const toast = inject(ToastSymbol);
  if (!toast) {
    console.warn('[useToast] No toast provider found, using no-op fallback');
    return { show: () => {}, message: ref(''), type: ref('') };
  }
  return toast;
}
