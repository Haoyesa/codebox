Component({
  properties: {
    original: { type: String, value: '' },
    optimized: { type: String, value: '' },
    editable: { type: Boolean, value: true },
  },
  methods: {
    onOriginalInput: function (e) { this.triggerEvent('originalChange', e.detail.value); },
    onOptimizedInput: function (e) { this.triggerEvent('optimizedChange', e.detail.value); },
  },
});