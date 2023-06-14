import { Form } from "react-bootstrap";
import React, { ChangeEventHandler } from "react";
import { SrInputBaseProps } from "./input";

export function SrDateTimeInput(props: SrInputBaseProps<string>) {
    let onChange: ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement> = (event) => {
        props.onChange(event.target.value);
    }
    // TODO: this may need to be an "input"
    return <Form.Control size="sm" className={'text-end'} type="datetime-local" {...props} onChange={onChange}></Form.Control>
}
