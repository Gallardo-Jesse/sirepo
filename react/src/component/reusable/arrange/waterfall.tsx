import React, { useEffect, useRef } from "react";
import { FunctionComponent } from "react";
import { Breakpoint, resolveBreakpoint, useWindowSize } from "../../../hook/breakpoint";
import { LayoutProps } from "../../../layout/layout";



export function WaterfallComponent(props: { 
    children: React.ReactNode,
    gutters: { vertical: string, horizontal: string },
    breakpoints: {[breakpointName: string]: number},
    padding: string
}) {
    function numColumnsForBreakpoint(breakpoint: Breakpoint) {
        let bins = 1; // TODO: place default somewhere
        if(!props.breakpoints) {
            //return bins;
            return bins;
        }
    
        let k = ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'];
        if(!k.includes(breakpoint)) {
            throw new Error(`unknown window breakpoint=${breakpoint}`)
        }
        for(let i = 0; i < k.indexOf(breakpoint); i++) {
            if(Object.keys(props.breakpoints).includes(k[i])) {
                bins = props.breakpoints[k[i]];
            }
        }
    
        return bins;
    }

    let windowSize = useWindowSize();
    let breakpoint = resolveBreakpoint(windowSize);
    let numColumns = numColumnsForBreakpoint(breakpoint);

    let containerRef = useRef<HTMLDivElement>();

    let fixupStyles = () => {
        if(containerRef.current) {
            let children = [...containerRef.current.children];
            children.map(c => c as HTMLElement).forEach(c => {
                c.style.width = "100%";
                c.style.padding = "0";
                c.style.marginBottom = props.gutters.vertical;
                c.style.boxSizing = "border-box";
                c.style.breakInside = "avoid";
            })
        }  
    }

    useEffect(() => {
        if(containerRef.current) {
            fixupStyles();
            let observer = new MutationObserver((mutations) => {
                fixupStyles();
            })
            observer.observe(containerRef.current, { childList: true });
            return () => observer.disconnect();
        }
        return () => {}
    })

    return (
        <>
            <div style={{
                listStyle: "none",
                columnGap: props.gutters.horizontal,
                padding: props.padding,
                columnCount: `${numColumns}`
            }} ref={containerRef}>
                {props.children}
            </div>
        </>
    )
};
