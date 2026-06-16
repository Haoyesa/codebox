Component({
  properties: {
    type: { type: String, value: 'primary' },
    size: { type: String, value: 'md' },
    block: { type: Boolean, value: false },
    disabled: { type: Boolean, value: false },
  },
  methods: {
    onTap: function (e) {
      if (this.data.disabled) return;
      this.triggerEvent('tap', e.detail);
    },
  },
});