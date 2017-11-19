import { React } from 'react';

const Navbar = () => {
    return (
        <nav className="navbar navbar-inverse navbar-fixed-top" role="navigation">
            <div className="container-fluid">
                <div className="navbar-header">
                    <button
                        type="button"
                        className="navbar-toggle collapsed"
                        data-toggle="collapse"
                        data-target=".navbar-collapse">
                        <span className="sr-only">Toggle navigation</span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                    </button>
                    <Link to="/">
                        <i className="fa fa-home"></i>
                        OWASP OWTF
                    </Link>
                </div>
                <div className="navbar-collapse collapse">
                    <ul className="nav navbar-nav navbar-right">
                        <li>
                            <Link to="/dashboard">
                                <i className="fa fa-tachometer"></i>
                                Dashboard
                            </Link>
                        </li>
                        <li>
                            <Link to="/targets">
                                <i className="fa fa-crosshairs"></i>
                                Targets
                            </Link>
                        </li>
                        <li>
                            <Link to="/workers">
                                <i className="fa fa-th-large"></i>
                                Workers
                            </Link>
                        </li>
                        <li>
                            <Link to="/worklist">
                                <i className="fa fa-bars"></i>
                                Worklist
                            </Link>
                        </li>
                        <li>
                            <Link to="/configuration">
                                <i className="fa fa-gears"></i>
                                Settings
                            </Link>
                        </li>
                        <li>
                            <Link to="/transactions">
                                <i className="fa fa-list-alt"></i>
                                Transactions
                            </Link>
                        </li>
                        <li>
                            <Link to="/help">
                                <i className="fa fa-link"></i>
                                Help
                            </Link>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}
