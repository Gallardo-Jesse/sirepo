import React from "react";
import { useContext } from "react";
import { CSchema } from "../../data/appwrapper";
import { WaterfallComponent } from "../reusable/arrange/waterfall";
import { Panel } from "../reusable/panel";

export function JspecRoot(props: {}) {
    let schema = useContext(CSchema);

    return (<>
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
                <Panel title={"Ion Beam"}>
                    <></>
                </Panel>
        </WaterfallComponent>
    </>)
}
