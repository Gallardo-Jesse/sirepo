import React from "react";
import { Dependency } from "../data/dependency";
import { LayoutProps, LayoutType, Layout } from "./layout";

export function LayoutWithSpacing<C, P>(Child: LayoutType<C, P>): LayoutType<C, P> {
    return class extends Child {
        constructor(config: C) {
            super(config);

            let childComponent = this.component;
            this.component = (props: LayoutProps<P>) => {
                let ChildComponent = childComponent;
                return (
                    <div className="sr-form-layout">
                        <ChildComponent {...props} />
                    </div>
                )
            }
        }
    }
}
