import React from 'react';

import {createMuiTheme, CssBaseline} from '@material-ui/core';
import {blue, deepOrange} from '@material-ui/core/colors';
import {MuiThemeProvider} from '@material-ui/core/styles';

import 'react-perfect-scrollbar/dist/css/styles.css';

import Header from 'components/Header';
import Routes from './Routes';

const gdgTheme = createMuiTheme({
  palette: {
    primary: blue,
    secondary: deepOrange,
    type: 'light',
  },
});
const App: React.FC = () => {
  return (
    <MuiThemeProvider theme={gdgTheme}>
      <CssBaseline />
      <Header />
      <main>
        <Routes />
      </main>
    </MuiThemeProvider>
  );
};

export default App;
