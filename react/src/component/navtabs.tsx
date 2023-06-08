import React, { useContext } from "react";
import { Nav } from "react-bootstrap";
import { Navigate, useParams, useResolvedPath, useRoutes } from "react-router";
import { Link } from "react-router-dom";
import { CRelativeRouterHelper, RelativeRouteHelper } from "../utility/route";
import { NavbarRightContainerId } from "./navbar";
import { Portal } from "./reusable/portal";

export type TabConfig = { title: string, path: string }
export type NavTabsProps = { tabs: TabConfig[], children?: React.ReactNode | React.ReactNode[] }

const CSelectedTab = React.createContext<string>(undefined);

export function TabsSwitcher (props: NavTabsProps) {
    let { tabName: selectedTabName } = useParams();
    let routerHelper = useContext(CRelativeRouterHelper);

    return (
        <>
            <Portal targetId={NavbarRightContainerId} className="order-1">
                <Nav variant="tabs" navbar={true} defaultActiveKey={selectedTabName}>
                    {
                        props.tabs.map(tab => {
                            let route = routerHelper.getRelativePath(tab.path);
                            return (
                                <Nav.Item key={tab.path}>
                                    <Nav.Link eventKey={`${tab.path}`} as={Link} href={`${tab.path}`} to={`${route}`}>
                                        {tab.title}
                                    </Nav.Link>
                                </Nav.Item>
                            )
                        })
                    }
                </Nav>
            </Portal>
            <CSelectedTab.Provider value={selectedTabName}>
                {props.children}
            </CSelectedTab.Provider>
        </>
    )
}

export function SrNavTab(props: { tab: string, children?: () => React.ReactNode | React.ReactNode[] }) {
    let selectedTabName = useContext(CSelectedTab);

    return (
        <>
            { props.children && selectedTabName === props.tab && props.children() }
        </>
    )
}

export function SrNavTabs(props: NavTabsProps) {
    if(props.tabs.length === 0) {
        throw new Error("navtabs component contained no tabs");
    }

    let firstTabName = props.tabs[0].path;

    let location = useResolvedPath('');

    let routeHelper = new RelativeRouteHelper(location);

    let routedElement = useRoutes([
        {
            path: '/',
            element: <Navigate to={`${firstTabName}`}></Navigate>
        },
        {
            path: ':tabName/*',
            element: <TabsSwitcher {...props}/>
        }
    ])

    return (
        <CRelativeRouterHelper.Provider value={routeHelper}>
            {routedElement}
        </CRelativeRouterHelper.Provider>
    )
}
