import {React} from 'react';
import {ReactDOM, render} from 'react-dom';
// Import routing components
import {Router, Route, Switch, withRouter} from 'react-router';
import Home from './Home/Home.js';
import Dashboard from './Dashboard/Dashboard.js';
import Transactions from './Transactions/Transactions.js';
import Report from './Report/Report.js';

var pageID = document.getElementById('root').childNodes[1].id;

if (pageID == 'home') {
  ReactDOM.render(
    <Home/>, document.getElementById('home'));
} else if (pageID == 'dashboard') {
  ReactDOM.render(
    <Dashboard/>, document.getElementById('dashboard'));
} else if (pageID == 'transactions') {
  ReactDOM.render(
    <Transactions/>, document.getElementById('transactions'));
} else if (pageID == 'report') {
  ReactDOM.render(
    <Report/>, document.getElementById('report'));
}
