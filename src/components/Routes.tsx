import React from 'react';
import {HashRouter, Route, Switch} from 'react-router-dom';

import Home from 'pages/Home';
import NotFound from 'pages/NotFound';

const Routes: React.FC = () => {
  return (
    <HashRouter>
      <Switch>
        <Route path="/" exact={true} component={Home} />
        <Route component={NotFound} />
      </Switch>
    </HashRouter>
  );
};

export default Routes;
