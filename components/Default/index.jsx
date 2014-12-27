var React = require("react");

require("./style.css");


// Require React-Router
var Router = require('react-router');
var Route = Router.Route;
var NotFoundRoute = Router.NotFoundRoute;
var DefaultRoute = Router.DefaultRoute;
var Link = Router.Link;
var RouteHandler = Router.RouteHandler;


var Default = React.createClass({
	render: function() {
		return <div>
		</div>;
	}
});

module.exports = Default;
