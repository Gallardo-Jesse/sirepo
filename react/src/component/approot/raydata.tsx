import React from "react";
import { useContext } from "react";
import { CSchema } from "../../data/appwrapper";
import { SrNavTab, SrNavTabs } from "../navtabs";
import { VerticalStack } from "../reusable/arrange/stack";
import { WaterfallComponent } from "../reusable/arrange/waterfall";
import { ModalPanel } from "../reusable/panel";


export function RaydataRoot(props: {}) {
    let schema = useContext(CSchema);


    return (
        <SrNavTabs tabs={[
            {
                path: "run-analysis",
                title: "Run Analysis"
            },
            {
                path: "analysis-queue",
                title: "Queue"
            }
        ]}>
            <WaterfallComponent 
                breakpoints={{
                    "sm": 1,
                    "md": 2,
                    "xl": 3
                }}
                gutters={{
                    horizontal: ".5em",
                    vertical: ".5em"
                }} 
                padding=".5em">
                <SrNavTab tab={"run-analysis"}>
                    {() => (
                        <>
                            <ModalPanel title={"Run Analysis"}>
                                <VerticalStack warp={"nowrap"}>
                                    {
                                        (() => {
                                            return <></>
                                        })()
                                    }
                                </VerticalStack>
                            </ModalPanel>
                        </>
                    )}
                </SrNavTab>
                <SrNavTab tab={"analysis-queue"}>
                    {() => (
                        <>
                        </>
                    )}
                </SrNavTab>
            </WaterfallComponent>
        </SrNavTabs>
    )
}
