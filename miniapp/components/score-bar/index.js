Component({
  properties: {
    label: { type: String, value: '' },
    value: { type: Number, value: 0 },
  },
  observers: {
    'value': function (v) {
      let level = 'low';
      if (v >= 80) level = 'high';
      else if (v >= 60) level = 'mid';
      this.setData({ level: level });
    },
  },
});