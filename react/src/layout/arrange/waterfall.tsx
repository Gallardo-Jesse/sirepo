import { FunctionComponent, } from "react";
import { mapProperties } from "../../utility/object";
import { LAYOUTS } from "../layouts";
import React from "react";
import "./waterfall.scss";
import { WaterfallComponent } from "../../component/reusable/arrange/waterfall";
import { SchemaLayout } from "../../data/schema";
import { Layout, LayoutProps } from "../layout";


export type WaterfallConfig = {
    items: SchemaLayout[],
    breakpoints?: {[breakpointName: string]: number},
    gutters?: {
        vertical?: string | number,
        horizontal?: string | number
    },
    padding: string | number
}

function formatValue(v: number | string) {
    if(typeof(v) === 'number') {
        return `${v}px`;
    }
    return v;
}

export class WaterfallLayout extends Layout<WaterfallConfig, {}> {
    children: Layout[];

    constructor(config: WaterfallConfig) {
        super(config);
        this.children = (config.items || []).map(schemaLayout => {
            return LAYOUTS.getLayoutForSchema(schemaLayout);
        });
    }

    component: FunctionComponent<{ [key: string]: any; }> = (props: LayoutProps<{}>) => {
        let c: JSX.Element[] = this.children.map((c, idx) => {
            let LayoutComponent = c.component;
            return <LayoutComponent key={idx}/>
        });

        return (
            <>
                <WaterfallComponent gutters={{
                    vertical: formatValue(this.config.gutters.vertical),
                    horizontal: formatValue(this.config.gutters.horizontal)
                }} padding={formatValue(this.config.padding)} breakpoints={this.config.breakpoints}>
                    {c}
                </WaterfallComponent>
            </>
        )
    };
}
