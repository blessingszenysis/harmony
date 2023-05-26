// @flow
import * as Zen from 'lib/Zen';

type Values = {
  id: string,
  axisLabelFill: string,
  axisLineStroke: string,
  axisTickStroke: string,
  backgroundColor: string,
  linesColorRange: $ReadOnlyArray<string>,
};

// light theme colors are similar to those generated by d3.schemeCategory10
// eslint-disable-next-line
// see https://github.com/d3/d3-scale-chromatic/blob/master/src/categorical/category10.js
// for more details
const LIGHT_THEME_COLOR_RANGE = [
  '#1f77b4',
  '#ff7f0e',
  '#2ca02c',
  '#d62728',
  '#9467bd',
  '#8c564b',
  '#e377c2',
  '#7f7f7f',
  '#bcbd22',
  '#17becf',
];

const DARK_THEME_COLOR_RANGE = [
  '#ed4fbb',
  '#eb4d70',
  '#f19938',
  '#6ce18b',
  '#fae856',
  '#f29b38',
  '#e64357',
  '#8386f7',
  '#3236b8',
];

class LineGraphTheme extends Zen.BaseModel<LineGraphTheme, Values> {
  static DarkTheme: Zen.Model<LineGraphTheme> = LineGraphTheme.create({
    id: 'dark',
    axisLabelFill: 'white',
    axisLineStroke: 'white',
    axisTickStroke: 'white',
    backgroundColor: '#27273f',
    linesColorRange: DARK_THEME_COLOR_RANGE,
  });

  static LightTheme: Zen.Model<LineGraphTheme> = LineGraphTheme.create({
    id: 'light',
    axisLabelFill: 'rgba(0,0,0,0.7)',
    axisLineStroke: 'rgba(0,0,0,0.7)',
    axisTickStroke: 'rgba(0,0,0,0.7)',
    backgroundColor: 'transparent',
    linesColorRange: LIGHT_THEME_COLOR_RANGE,
  });

  static Themes: { +[string]: Zen.Model<LineGraphTheme> } = {
    [LineGraphTheme.DarkTheme.id()]: LineGraphTheme.DarkTheme,
    [LineGraphTheme.LightTheme.id()]: LineGraphTheme.LightTheme,
  };
}

export default ((LineGraphTheme: $Cast): Class<Zen.Model<LineGraphTheme>>);
