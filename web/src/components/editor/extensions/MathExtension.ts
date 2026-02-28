import { Node, Extension, mergeAttributes } from '@tiptap/core'
import {
    mathPlugin,
    mathBackspaceCmd,
    makeBlockMathInputRule,
    makeInlineMathInputRule,
    REGEX_INLINE_MATH_DOLLARS,
    REGEX_BLOCK_MATH_DOLLARS
} from '@benrbray/prosemirror-math'

export const MathInline = Node.create({
    name: 'math_inline',
    group: 'inline',
    content: 'text*',
    inline: true,
    atom: true,

    parseHTML() {
        return [
            { tag: 'math-inline' },
        ]
    },

    renderHTML({ HTMLAttributes }) {
        return ['math-inline', mergeAttributes(HTMLAttributes), 0]
    },
})

export const MathDisplay = Node.create({
    name: 'math_display',
    group: 'block',
    content: 'text*',
    atom: true,
    code: true,

    parseHTML() {
        return [
            { tag: 'math-display' },
        ]
    },

    renderHTML({ HTMLAttributes }) {
        return ['math-display', mergeAttributes(HTMLAttributes), 0]
    },
})

import { inputRules } from 'prosemirror-inputrules'

export const MathExtension = Extension.create({
    name: 'mathExtension',

    addProseMirrorPlugins() {
        return [
            mathPlugin,
            inputRules({
                rules: [
                    makeInlineMathInputRule(REGEX_INLINE_MATH_DOLLARS, this.editor.schema.nodes.math_inline),
                    makeBlockMathInputRule(REGEX_BLOCK_MATH_DOLLARS, this.editor.schema.nodes.math_display),
                ]
            })
        ]
    },

    addKeyboardShortcuts() {
        return {
            Backspace: () => this.editor.commands.command(({ tr, dispatch }) => {
                if (dispatch) {
                    return mathBackspaceCmd(this.editor.state, dispatch, this.editor.view)
                }
                return false
            }),
        }
    }
})
